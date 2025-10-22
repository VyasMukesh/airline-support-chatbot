from django.test import Client
import json

def run():
    c = Client()
    print('Process before verify ->', c.post('/process', data=json.dumps({'message':'cancel flight'}), content_type='application/json').json())
    print('Verify NOPE ->', c.post('/api/verify_pnr', data=json.dumps({'pnr':'NOPE'}), content_type='application/json').json())
    print('Verify TEST123 ->', c.post('/api/verify_pnr', data=json.dumps({'pnr':'TEST123'}), content_type='application/json').json())
    print('Process after verify ->', c.post('/process', data=json.dumps({'message':'flight status'}), content_type='application/json').json())

if __name__ == '__main__':
    run()
