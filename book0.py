import requests
def main():
	
	res = requests.get("https://www.goodreads.com/book/id_to_work_id/1842,1867?key=prsUZ2NatVUJ26Otr5cgYQ")
	print(res.xml())
	
	
main()