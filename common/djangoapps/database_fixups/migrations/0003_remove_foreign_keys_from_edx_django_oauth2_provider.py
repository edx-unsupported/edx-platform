# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

"""
The `edx-django-oauth2-provider` has been deprecated in favor of `django-oauth-toolkit`.
Its tables however persist in database. They have foreign key dependancy with `auth_user.id`. Django does
not resolves this constratint and we are unable to remove users.

This migration drops the foreign key relation between the 4 tables created by `edx-django-oauth2-provider`
and `auth_user`.
"""


class Migration(migrations.Migration):

    dependencies = [
        ('database_fixups', '0002_remove_foreign_keys_from_progress_extensions'),
    ]

    operations = [
        migrations.RunSQL(
            """
            -- Drop a procedure if it already exists - safety check.
            DROP PROCEDURE IF EXISTS drop_foreign_key_from_oauth2_table;

            -- We are dropping constraints from 4 tables, so we create a temporary procedure to avoid code repetition.
            CREATE PROCEDURE drop_foreign_key_from_oauth2_table(given_table VARCHAR(64))
            BEGIN
                -- Getting the foreign key that refernces to auth_user table
                SET @auth_foreign_key = (
                    SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE REFERENCED_TABLE_SCHEMA='edxapp'
                        AND REFERENCED_TABLE_NAME='auth_user'
                        AND TABLE_NAME=given_table
                );

                IF @auth_foreign_key IS NOT NULL THEN
                    -- DROP the existing foreign key.
                    SET @statement = CONCAT('ALTER TABLE ', given_table, ' DROP FOREIGN KEY ', @auth_foreign_key);
                    PREPARE stmt FROM @statement;
                    EXECUTE stmt;
                    DEALLOCATE PREPARE stmt;
                ELSE
                    -- Raise custom error for having clearer logs in case of a failure.
                    SET @error_message = CONCAT('Cannot find foreign key in ', given_table, ' table.');
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = @error_message;
                END IF;

            END;

            -- Call temporary procedure on relevant tables.
            CALL drop_foreign_key_from_oauth2_table('oauth2_client');
            CALL drop_foreign_key_from_oauth2_table('oauth2_grant');
            CALL drop_foreign_key_from_oauth2_table('oauth2_accesstoken');
            CALL drop_foreign_key_from_oauth2_table('oauth2_refreshtoken');

            -- Clean up.
            DROP PROCEDURE IF EXISTS drop_foreign_key_from_oauth2_table;
        """,
            reverse_sql="""
            ALTER TABLE `oauth2_client` ADD FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
            ALTER TABLE `oauth2_grant` ADD FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
            ALTER TABLE `oauth2_accesstoken` ADD FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
            ALTER TABLE `oauth2_refreshtoken` ADD FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
        """,
        )
    ]
