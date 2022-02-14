import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from a1.models import Client, User


class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self._create_subscribers()
        self._create_subscribersSMS()



    def _create_subscribers(self):
        sql = self._create_query_for_subscribers()
        self._add_correct_users_to_db(sql)
        sql = self._get_query_for_conflict_subscribers()
        conflicts = self._get_conflicts(sql)
        duplicated = self._get_dupicated_phone_in_clents()
        write_data_to_csv_file('subscriber_conflicts.csv', conflicts)
        write_data_to_csv_file('client_duplicated_phones.csv', duplicated)

    def _create_subscribersSMS(self):
        sql = self._create_query_for_subscribersSMS()
        self._add_correct_users_to_db(sql)
        sql = self._get_query_for_conflict_subscribersSMS()
        conflicts = self._get_conflicts(sql)
        write_data_to_csv_file('subscriberSMS_conflicts.csv', conflicts)




    def _create_query_for_subscribers(self):
        user_dont_exist = "sub.email NOT IN (SELECT email FROM a1_user WHERE email IS NOT null)"
        no_client_with_matching_phone = "cln.phone NOT IN (SELECT phone FROM a1_user)"
        phone_not_duplicate_in_client = """cln.phone NOT IN (SELECT phone FROM (SELECT phone, COUNT(*) 
                                                                                FROM a1_client 
                                                                                GROUP BY phone 
                                                                                HAVING COUNT(*) > 1) AS t)"""

        query = f"""
                SELECT sub.id, sub.email, cln.phone, sub.gdpr_consent
                FROM a1_subscriber sub LEFT JOIN a1_client cln ON sub.email = cln.email 
                WHERE 
                {user_dont_exist} AND (
                {no_client_with_matching_phone} AND 
                {phone_not_duplicate_in_client} OR
                cln.phone IS null )
        """
        return query

    def _create_query_for_subscribersSMS(self):
        user_dont_exist = "sub.phone not in (select phone from a1_user where phone is not null)"
        no_client_with_matching_mail = "cln.email not in (select email from a1_user)"
        mail_not_duplicate_in_client = """ cln.email not in (select email from (SELECT email, COUNT(*) 
                                                                                FROM a1_client 
                                                                                GROUP BY email 
                                                                                HAVING COUNT(*) > 1) as t)"""
        query = f"""
                        SELECT sub.id, sub.phone, cln.email, sub.gdpr_consent
                        FROM a1_subscribersms sub LEFT JOIN a1_client cln ON sub.phone = cln.phone
                        WHERE 
                        {user_dont_exist} AND (
                        {no_client_with_matching_mail} AND 
                        {mail_not_duplicate_in_client} OR
                        cln.phone IS null )
                """
        return query

    def _get_query_for_conflict_subscribersSMS(self):
        sql = """
                           SELECT sub.id, sub.phone, cln.email
                           FROM a1_subscribersms sub 
                           JOIN a1_client cln ON sub.phone = cln.phone 
                           JOIN a1_user u on cln.email = u.phone
                           where u.email != cln.email
                       """
        return sql


    def _add_correct_users_to_db(self, query):
        clients = Client.objects.raw(query)
        users = [User(email=item.email, phone=item.phone, gdpr_consent=item.gdpr_consent)
                 for item in clients]
        User.objects.bulk_create(users)

    def _get_query_for_conflict_subscribers(self):
        sql = """
                    SELECT sub.id, sub.email, cln.phone
                    FROM a1_subscriber sub 
                    JOIN a1_client cln ON sub.email = cln.email 
                    JOIN a1_user u on cln.phone = u.phone
                    where u.email != cln.email
                """
        return sql

    def _get_conflicts(self, sql):
        clients = Client.objects.raw(sql)
        return [(client.id, client.email) for client in clients]

    def _get_dupicated_phone_in_clents(self):
        sql = """WITH duplicated_phone as (select phone from 
						                    (SELECT phone, COUNT(*) 
						                     FROM a1_client 
						                     GROUP BY phone 
						                     HAVING COUNT(*) > 1) as t)
                    SELECT id, email, phone from 
                    a1_client where a1_client.phone in (select phone from duplicated_phone) Order by phone;
                """
        clients = Client.objects.raw(sql)
        return [(client.id, client.email, client.phone) for client in clients]


def write_data_to_csv_file(filename, collection):
    print([item for item in collection])
    with open(filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';', )
        [writer.writerow(row) for row in collection]
