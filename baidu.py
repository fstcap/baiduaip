#import argpare
#parser = argpare.ArgumentParser()
#parser.add_argument("--model",type=str,defualt="dense")
#parser.add_argument("--url",type=str,defualt="")
#args = parser.parse_args()
#print("args---------",args['url'])

#import sys
#print("args---------",sys.argv[1])
#with open(sys.argv[1],"rb") as f:
#    img = f.read()

#我进行了修改
import os
#import numpy as np
import base64
import json
import requests
import re

class SetResponse:
    status = 1
    error = 0
    msg = ''
    data = {}
    def get_attribute(self):
        return self.__dict__
    def set_status(self,status,msg,data):
        self.status = status
        self.msg = msg
        self.data = data
        return {'status':status,'msg':msg,'data':data}
    def set_error(self,error,msg,data={}):
        self.error = error
        self.msg = msg
        self.data = data
        return {'error':error,'msg':msg,'data':data}


#本地储存token
class DocumentRw:
    path_dir:''
    def __init__(self):
        main_path = os.getcwd()
        self.path_dir = f'{main_path}'
    def __enter__(self):
        print('__enter__()_greate_document is call!')
        return self
    def mkdir(self,path):
        dir_addr = f'{self.path_dir}/{path}'
        folder = os.path.exists(dir_addr)
        if folder:
            return '---  There is this folder!  ---'
        os.makedirs(dir_addr)
        return '---  new folder...  ---'
    def writetxt(self,context,path,name):
        self.mkdir(path)
        with open(f'{self.path_dir}/{path}/{name}','w') as txt_file:
            txt_file.write(context)
    def readtxt(self,path,name):
        res = SetResponse()
        folder = os.path.exists(f'{self.path_dir}/{path}/{name}')
        if not folder:
            print(str(res.set_error('1005',f'No token {name}')))
            return res.set_error('1005',f'No token {name}')
        with open(f'{self.path_dir}/{path}/{name}','r') as txt_file:
            txt_context = txt_file.read()
        return res.set_status(1,txt_context,{})
    def __exit__(self, exc_type, exc_value, traceback):
        print('__exit__()_create_document is call!')
        print(f'type:{exc_type}')
        print(f'value:{exc_value}')
        print(f'trace:{traceback}')
        print('__exit()__-create_document is call!')

#获取图片信息
class GetMessage:
    image = ''
    access_token = ''
    def __enter__(self):
        print('__enter__()_get_message is call!')
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        print('__exit__()_get_message is call!')
        print(f'type:{exc_type}')
        print(f'value:{exc_value}')
        print(f'trace:{traceback}')
        print('__exit()__-get_message is call!')

    def serve_request_token(self,callback):
        token_url = 'https://aip.baidubce.com/oauth/2.0/token'
        client_data = {
                "grant_type":"client_credentials",
                "client_id":"", #client_id
                "client_secret":""}
        res = requests.post(token_url,data=client_data)
        res_body = json.loads(res.text)
        res_status = SetResponse()
        if 'access_token' not in res_body:
            return res_status.set_error(1007,res_body['error_description'])
        with DocumentRw() as doc:
            create_doc = doc.writetxt(res_body['access_token'],'token','token_aip.txt')
        self.access_token = res_body['access_token']
        return callback()
        #return res_status.set_status(1,'Geted token',{'access_token':res_body['access_token']})
    
    def request_aip(self): 
        res_status = SetResponse()
        ocr_url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/vat_invoice'
        headers = {"Content-Type":"application/x-www-form-urlencoded"}
        params = {"access_token":self.access_token}
        image_base64 = self.image
        body = {"accuracy":"hight","image":image_base64}
        res = requests.post(ocr_url,headers=headers,params=params,data=body)
        res_json = json.loads(res.text)
        print("获取api图片信息",str(res_json))
        if'error_code'in res_json and(int(res_json['error_code'])== 110 or int(res_json['error_code'])==111):
            return self.serve_request_token(self.request_aip)
        elif 'error_code' in res_json:
        
            return res_status.set_error(res_json['error_code'],res_json['error_msg'])
        else:
            return res_json

    def serve_request_img(self,image):

        self.image = image
        
        res_status = SetResponse()
        with DocumentRw() as doc:
            read_doc = doc.readtxt('token','token_aip.txt')
        if 'error' in read_doc:
            return self.serve_request_token(self.request_aip)

        else:
            self.access_token = read_doc['msg']
            return self.request_aip()

#发票在线校验
class ValidationTicky:
    app_key = ''
    app_secret = ''
    token_url = 'https://open.leshui365.com/getToken'
    fapiao_url = 'https://open.leshui365.com/api/invoiceInfoForCom'
    access_token = ''
    InvoiceCode = ''
    InvoiceNum = ''
    InvoiceDate = ''
    CheckCode = ''

    def __enter__(self):
        print('__enter__()_ValidationTicky is call!')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print('__exit__()_ValidationTicky is call!')
        print(f'type:{exc_type}')
        print(f'value:{exc_value}')
        print(f'trace:{traceback}')
        print('__exit()__-ValidationTicky is call!')

    def get_token(self,callback):
        res_status = SetResponse()
        param = {'appKey':self.app_key,'appSecret':self.app_secret}  #appSecret 
        res = requests.get(self.token_url,params=param)
        res_json = json.loads(res.text)
        
        if 'error' not in res_json and 'token' in res_json:
            token_val = res_json['token']
            with DocumentRw() as doc:
                doc.writetxt(token_val,'token','token_val.txt')
            self.access_token = token_val
            print('发票校验读取本地token失败请求在线token',str(token_val))
            return callback()
        else:
            return res_status.set_error(1004,res_json['error'])

    def get_fapiao(self):
        res_status = SetResponse()
        fp_data = {"invoiceCode": self.InvoiceCode,  # 发票代码
               "invoiceNumber": self.InvoiceNum,  # 发票号码
               "billTime": self.InvoiceDate,  # 开票时间
               "checkCode": self.CheckCode,  # 校验码
               "invoiceAmount": '',  # totalAmount
               "token": self.access_token  # 授权码，token取get_token返回值
               }
        headers = {"Content-Type":"application/x-www-form-urlencoded"}
        res = requests.post(self.fapiao_url,headers=headers,data=fp_data)
        print('发票校验返回数据',str(res.text))
        val_obj = json.loads(res.text)
        if 'error' not in val_obj and val_obj['RtnCode'] == '00' and val_obj['resultCode'] == '1000':

            check_attr = {'InvoiceCode':self.InvoiceCode,
                    'InvoiceNum':self.InvoiceNum,
                    'InvoiceDate':self.InvoiceDate,
                    'CheckCode':self.CheckCode}

            return res_status.set_status(1,'Success',check_attr)
        elif 'error' in val_obj and val_obj['error'] == 'token error':
            print(str(val_obj))
            return self.get_token(self.get_fapiao)
        else:
            if "resultMsg" in val_obj:
                msg = val_obj["resultMsg"]
            else:
                msg = "validation fail"
            return res_status.set_error(1006,msg,{})

    def match_ticky(self,InvoiceCode, InvoiceNum, InvoiceDate, CheckCode):
        self.InvoiceCode = InvoiceCode
        self.InvoiceNum = InvoiceNum
        self.InvoiceDate = InvoiceDate
        self.CheckCode = CheckCode
        res = SetResponse()
        with DocumentRw() as doc:
            doc_obj = doc.readtxt('token','token_val.txt')
        
        if 'error' in doc_obj:
            return self.get_token(self.get_fapiao)
        else:
            print('发票校验读取本地token成功',doc_obj)
            self.access_token = doc_obj['msg']
            return self.get_fapiao()

from flask import Flask,request,flash,jsonify,make_response
from flask_cors import CORS

class ResponeBody:
    ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])
    request = {}
    def allowd_file(self,filename):
        return '.' in filename and filename.rsplit('.',1)[1].lower() in self.ALLOWED_EXTENSIONS
    def judge_type(self,request):
        res = SetResponse()
        self.request = request
        form_data = request.form
        if str(form_data['type']) == '1':
            if re.search('^(http|https)://(.)+\.(png|jpg|jpeg)$',form_data['image']) == None:
                return jsonify(res.set_error(1009,'Url Not Correct'))
            response = requests.get(form_data['image'],stream=True)
            print("-----status-----",response.status_code)
            if str(response.status_code) != '200':
                return jsonify(res.set_error(1010,'GET nothing'))
            return self.GetImgMsg(base64.b64encode(response.content).decode('utf-8'))
        else:
            if 'image' not in self.request.files:
                return jsonify(res.set_error(1001,'No file part'))
            file = self.request.files['image']
            if file.filename == '':
                return jsonify(res.set_error(1002,'No selected file'))
            if not file or not self.allowd_file(file.filename):
                return jsonify(res.set_error(1003,'choose pdf,png,jpg,jpeg')) 
            return self.GetImgMsg(base64.b64encode(file.stream.read()).decode())
    def GetImgMsg(self,image):
        with GetMessage() as got_message:
            data = got_message.serve_request_img(image)
        if 'error' in data:
            return jsonify(data)
        result = data['words_result']
        return self.val_fapiao(result['InvoiceCode'],result['InvoiceNum'],result['InvoiceDate'],result['CheckCode'])
    
    def val_fapiao(self,InvoiceCode,InvoiceNum,InvoiceDate,CheckCode):
        res = SetResponse()
        CheckCode = CheckCode[-6:]
        InvoiceDate = InvoiceDate.replace('年','-').replace('月','-').replace('日','')
        print(f"InvoiceCode{InvoiceCode},{InvoiceNum},{InvoiceDate},{CheckCode}")
        with ValidationTicky() as valticky:
            validate = valticky.match_ticky(InvoiceCode,InvoiceNum,InvoiceDate,CheckCode)
        print(str(validate))
        if 'error' in validate:
            realize_data = {"InvoiceCode":InvoiceCode,"InvoiceNum":InvoiceNum,"InvoiceDate":InvoiceDate,"CheckCode":CheckCode}
            return jsonify(res.set_error(validate['error'],validate['msg'],realize_data))
        else:
            return jsonify(validate)

#创建api
def flask_api():
    #UPLOAD_FOLDER = f'{os.getcwd()}/uploads/'
    #rand_arr = np.random.randint(0,9,10)
    #sec_key = ''.join([str(x) for x in rand_arr])
    #print('sec_key---------',sec_key)

    app = Flask(__name__)
    #app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    #app.secret_key = sec_key
    #CORS(app,supports_credentials=True)

    @app.route('/ocr/val',methods=['GET', 'POST'])
    def get_file():
        res = SetResponse()
        form_data = request.form
        response = ResponeBody()
        if 'methods' in form_data and 'type' in form_data:
            if str(form_data['methods'])=='1'and'data'in form_data and'InvoiceCode'in form_data['data']:
                print("------------data--------------",str(form_data['data']))
                print(type(form_data['data']))
                data = json.loads(str(form_data['data']))
                return response.val_fapiao(str(data["InvoiceCode"]),str(data["InvoiceNum"]),str(data["InvoiceDate"]),str(data["CheckCode"]))
            elif str(form_data['methods']) == '0':
                return response.judge_type(request)
        else:
            return jsonify(res.set_error(1008,'loss vali params'))
    '''
    @app.after_request
    def af_request(resp):
        resp = make_response(resp)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Methods'] = 'GET,POST,OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
        return resp
    '''    
    return app

app = flask_api()
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=5000,threaded=True)

