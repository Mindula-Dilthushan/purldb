# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-10 23:54
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packagedb', '0030_auto_20190107_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='vcs_url',
            field=models.CharField(blank=True, help_text='a URL to the VCS repository in the SPDX form of: "git", "svn", "hg", "bzr", "cvs", https://github.com/nexb/scancode-toolkit.git@405aaa4b3 See SPDX specification "Package Download Location" at https://spdx.org/spdx-specification-21-web-version#h.49x2ik5 ', max_length=1024, null=True),
        ),
    ]
