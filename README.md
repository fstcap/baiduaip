百度aip增值税发票和国税局校验
api http://10.114.18.147:8000/ocr/val
Request:

	methods:POST
	headers:Content-Type=application/x-www-form-urlencoded
	body(form-data):type=(0/1) #0:image = file ;1:image=url
			image= (rely on 'type')
			methods = (0/1) 
			data={
				'InvoiceCode':'',
				'InvoiceNum':'',
				'InvoiceDate':'',  #(xxxx-xx-xx)
				'CheckCode':''
				}	#(rely on 'methods' )
				
Response:
	status:1(1:success)
	msg:''(about none)
	data:{}
	

Error:
	error:1001 - 'No file part'        
	      1002 - 'No selected file'
	      1003 - 'Choose png,jpg,jpeg'
	      1004 - 'Get token val fail'       #税务局token
	      1005 - 'No token file'
	      1006 - 'No match'
	      1007 - 'Get token aip fail'	#百度token	
	      1008 - 'loss vali params'
	      1009 - 'Url Not Correct'
	      百度错误码：https://ai.baidu.com/docs#/OCR-API/58fd45dd
	      
