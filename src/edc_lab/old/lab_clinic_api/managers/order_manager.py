from django.db.models import Manager


class OrderManager(Manager):
    def get_by_natural_key(self, order_identifier):
        return self.get(order_identifier=order_identifier)

    def flag_duplicates(self):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""
            SELECT aliquot_id
            FROM lab_clinic_api_order
            GROUP BY aliquot_id
            HAVING count(aliquot_id) > 1""")
        result_list = []
        for row in cursor.fetchall():
            for order in self.filter(aliquot_id=row[0]):
                order.status = 'DUPLICATE'
                order.save_base()
                result_list.append(order)
        return result_list
