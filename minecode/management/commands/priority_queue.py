#
# Copyright (c) nexB Inc. and others. All rights reserved.
# purldb is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/purldb for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import hashlib
import logging
import signal
import sys
import time

from django.db import transaction
from django.utils import timezone
from packagedcode.maven import get_urls
from packagedcode.maven import _parse
from packagedcode.maven import get_maven_pom
from packageurl import PackageURL
import requests

from minecode.management.commands import get_error_message
from minecode.management.commands import VerboseCommand
from minecode.management.commands.run_map import merge_or_create_package
from minecode.models import PriorityResourceURI
from minecode.models import ScannableURI
from packagedb.models import PackageRelation


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.INFO)

TRACE = False
if TRACE:
    logger.setLevel(logging.DEBUG)

# sleep duration in seconds when the queue is empty
SLEEP_WHEN_EMPTY = 10

MUST_STOP = False


def stop_handler(*args, **kwargs):
    """
    Signal handler to set global variable to True.
    """
    global MUST_STOP
    MUST_STOP = True


signal.signal(signal.SIGTERM, stop_handler)


class Command(VerboseCommand):
    help = 'Run a Package request queue.'

    def handle(self, *args, **options):
        """
        Get the next processable PriorityResourceURI and start the
        processing. Loops forever and sleeps a short while if there are
        no PriorityResourceURI left to process.
        """

        global MUST_STOP

        sleeping = False
        processed_counter = 0

        while True:
            if MUST_STOP:
                logger.info('Graceful exit of the request queue.')
                break

            with transaction.atomic():
                priority_resource_uri = PriorityResourceURI.objects.get_next_request()

            if not priority_resource_uri:
                # Only log a single message when we go to sleep
                if not sleeping:
                    sleeping = True
                    logger.info('No more processable request, sleeping...')

                time.sleep(SLEEP_WHEN_EMPTY)
                continue

            sleeping = False

            # process request
            logger.info('Processing {}'.format(priority_resource_uri))
            try:
                errors = process_request(priority_resource_uri)
            except Exception as e:
                errors = 'Error: Failed to process PriorityResourceURI: {}\n'.format(
                    repr(priority_resource_uri))
                errors += get_error_message(e)
            finally:
                if errors:
                    priority_resource_uri.processing_error = errors
                    logger.error(errors)
                priority_resource_uri.processed_date = timezone.now()
                priority_resource_uri.wip_date = None
                priority_resource_uri.save()
                processed_counter += 1

        return processed_counter


def process_request(priority_resource_uri):
    """
    TODO: move this to Maven visitor/mapper
    """
    package_url = priority_resource_uri.uri
    purl = PackageURL.from_string(package_url)
    has_version = bool(purl.version)
    error = ''
    if has_version:
        urls = get_urls(
            namespace=purl.namespace,
            name=purl.name,
            version=purl.version,
            qualifiers=purl.qualifiers
        )
        # Get and parse POM info
        pom_url = urls['api_data_url']
        response = requests.get(pom_url)
        if not response:
            msg = 'Package does not exist on maven: ' + repr(package_url)
            error += msg + '\n'
            logger.error(msg)
            return error

        # Create Package from POM info
        pom_contents = str(response.content)
        pom = get_maven_pom(text=pom_contents)
        package = _parse(
            'maven_pom',
            'maven',
            'Java',
            text=pom_contents
        )

        # Create Parent Package, if available
        parent_package = None
        if (
            pom.parent
            and pom.parent.group_id
            and pom.parent.artifact_id
            and pom.parent.version.version
        ):
            parent_urls = get_urls(
                namespace=pom.parent.group_id,
                name=pom.parent.artifact_id,
                version=str(pom.parent.version.version),
                qualifiers={}
            )
            # Get and parse parent POM info
            parent_pom_url = parent_urls['api_data_url']
            response = requests.get(parent_pom_url)
            if not response:
                msg = 'Parent Package does not exist on maven: ' + repr(package_url)
                error += msg + '\n'
                logger.error(msg)
            parent_pom_contents = str(response.content)
            parent_package = _parse(
                'maven_pom',
                'maven',
                'Java',
                text=parent_pom_contents
            )

        if parent_package:
            check_fields = (
                'license_expression',
                'homepage_url',
                'parties',
            )
            for field in check_fields:
                # If `field` is empty on the package we're looking at, populate
                # those fields with values from the parent package.
                if not getattr(package, field):
                    value = getattr(parent_package, field)
                    setattr(package, field, value)

        # If sha1 exists for a jar, we know we can create the package
        # Use pom info as base and create packages for binary and source package

        # Check to see if binary is available
        binary_package = None
        download_url = urls['repository_download_url']
        binary_sha1_url = f'{download_url}.sha1'
        response = requests.get(binary_sha1_url)
        if response.ok:
            # Create Package for binary package, if available
            sha1 = response.text.strip()
            sha1 = validate_sha1(sha1)
            if not sha1:
                response = requests.get(download_url)
                if response:
                    sha1_hash = hashlib.new('sha1', response.content)
                    sha1 = sha1_hash.hexdigest()
                else:
                    sha1 = priority_resource_uri.sha1
            package.sha1 = sha1
            package.download_url = download_url
            binary_package, _, _, _ = merge_or_create_package(package, visit_level=0)
        else:
            msg = 'Failed to retrieve binary JAR: ' + repr(package_url)
            error += msg + '\n'
            logger.error(msg)

        # Submit packages for scanning
        if binary_package:
            uri = binary_package.download_url
            _, scannable_uri_created = ScannableURI.objects.get_or_create(
                uri=uri,
                package=binary_package,
            )
            if scannable_uri_created:
                logger.debug(' + Inserted ScannableURI\t: {}'.format(uri))

        # Check to see if the sources are available
        purl.qualifiers['classifier'] = 'sources'
        sources_urls = get_urls(
            namespace=purl.namespace,
            name=purl.name,
            version=purl.version,
            qualifiers=purl.qualifiers
        )
        source_package = None
        download_url = sources_urls['repository_download_url']
        sources_sha1_url = f'{download_url}.sha1'
        response = requests.get(sources_sha1_url)
        if response.ok:
            # Create Package for source package, if available
            sha1 = response.text.strip()
            sha1 = validate_sha1(sha1)
            if not sha1:
                response = requests.get(download_url)
                if response:
                    sha1_hash = hashlib.new('sha1', response.content)
                    sha1 = sha1_hash.hexdigest()
                else:
                    sha1 = None
            package.sha1 = sha1
            package.download_url = download_url
            package.repository_download_url = download_url
            package.qualifiers['classifier'] = 'sources'
            source_package, _, _, _ = merge_or_create_package(package, visit_level=0)
        else:
            msg = 'Failed to retrieve sources JAR: ' + repr(package_url)
            error += msg + '\n'
            logger.error(msg)

        if source_package:
            uri = source_package.download_url
            _, scannable_uri_created = ScannableURI.objects.get_or_create(
                uri=uri,
                package=source_package,
            )
            if scannable_uri_created:
                logger.debug(' + Inserted ScannableURI\t: {}'.format(uri))

        if source_package and binary_package:
            make_relationship(
                from_package=source_package,
                to_package=binary_package,
                relationship=PackageRelation.Relationship.SOURCE_PACKAGE
            )

        return error
    else:
        pass


def make_relationship(
    from_package, to_package, relationship
):
    """
    from scio
    """
    return PackageRelation.objects.create(
        from_package=from_package,
        to_package=to_package,
        relationship=relationship,
    )

def validate_sha1(sha1):
    if sha1 and len(sha1) != 40:
        logger.warning(
            f'Invalid SHA1 length ({len(sha1)}): "{sha1}": SHA1 ignored!'
        )
        sha1 = None
    return sha1
