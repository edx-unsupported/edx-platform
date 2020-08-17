# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

"""
The `progress-edx-platform-extensions` has been deprecated in favor of `edx-completion`.
The requirement was removed in the commit linked as (1) below. However its migration (2) had not been reverted.
That migration used `auth_user.id` as the foreign key in its models (3), but Django does not resolve this constraint
between existing tables anymore, because the model has been removed.
Therefore we need to drop the tables related to deprecated application in order to be able to remove users properly.

Because of some performance concerns, deletion is implemented in (4).
This migration drops only foreign keys from deprecated tables.
If ran twice (for any reason), it will raise a custom error for better visibility that these keys do not exist.

(1) https://github.com/edx-solutions/edx-platform/commit/59bf3efe71533de53b60bd979517e889d18a96bb
(2) https://github.com/edx-solutions/progress-edx-platform-extensions/blob/master/progress/migrations/0001_initial.py
(3) https://github.com/edx-solutions/progress-edx-platform-extensions/blob/master/progress/models.py
(4) https://github.com/edx-solutions/edx-platform/pull/1862
"""


class Migration(migrations.Migration):

    dependencies = [
        ('database_fixups', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL("""
            -- Drop a procedure if it already exists - safety check.
            DROP PROCEDURE IF EXISTS drop_foreign_key_from_table;

            -- We are dropping constraints from 3 tables, so we create a temporary procedure to avoid code repetition.
            CREATE PROCEDURE drop_foreign_key_from_table(given_table VARCHAR(64))
            BEGIN
                -- Find the ID of the foreign key (there is only one per table, otherwise it would fail).
                SET @foreign_key = (
                    SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                    WHERE TABLE_NAME = given_table AND CONSTRAINT_TYPE = 'FOREIGN KEY'
                );
                IF @foreign_key IS NOT NULL THEN
                    -- Prepare query (MySQL does not allow embedding queries in a standard way here).
                    SET @statement = CONCAT('ALTER TABLE ', given_table, ' DROP FOREIGN KEY ', @foreign_key);
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
            CALL drop_foreign_key_from_table('progress_coursemodulecompletion');
            CALL drop_foreign_key_from_table('progress_studentprogress');
            CALL drop_foreign_key_from_table('progress_studentprogresshistory');

            -- Clean up.
            DROP PROCEDURE IF EXISTS drop_foreign_key_from_table;
        """)
    ]
