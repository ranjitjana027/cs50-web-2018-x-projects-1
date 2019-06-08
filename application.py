import os,requests


from flask import Flask, render_template, request,session, jsonify, flash, url_for, redirect
from flask_session import Session
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker

app=Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)




engine=create_engine(os.getenv("DATABASE_URL")) #"postgresql://postgres:ranjana99@localhost:5432/postgres"
db=scoped_session(sessionmaker(bind=engine))


'''@app.route('/signup')
def index():
	if 'user' in session:
		return "Logged in as "+session['user'].username+ "<br><a href='/'>Click to Search</a>"
		return redirect('/')
		
	return render_template("register.html")
'''

@app.route('/register', methods=["GET","POST"])
def register():
	if 'user' in session:
		return "Logged in as "+session['user'].email+ "<br><a href='/'>Click to Search</a>"
		#return redirect('/')
	if request.method=='POST':
		email=request.form.get("email")
		name=email.split('@')[0]
		password=request.form.get("password")
		re_password=request.form.get('re_password')
		if password!=re_password:
			return render_template("register.html", message="Passwords didn\'t match")
		try:
			db.execute("insert into user_login_details(email,username,password) values (:email,:username,:password)",{"email":email,"username":name,"password":password})
			db.commit()
			return render_template("success.html")
		except :
			return render_template("register.html", message="Username alreday exists!")

	return render_template("register.html")

'''
@app.route('/login')
def login():
	return render_template("login.html")
'''
@app.route('/logout')
def logout():
	session.pop('user',None)
	return redirect(url_for('search'))

@app.route('/login', methods=["GET","POST"])
def login():
	if 'user' in session:
		return "Already Logged in as "+session['user'].email+ "<br><a href='/'>Click to Search</a> <br><a href='/logout'>Click here to logout.</a>"
		return redirect('/')
	#session["user"]=[]
	if request.method=='POST':
		email=request.form.get("email")
		password=request.form.get("password")
		details=db.execute("select * from user_login_details where email=:email and password=:password",{"email":email,"password":password}).fetchone()
		if details is None:
			return render_template('login.html',message="No such account. Try again.")
		else :
			session["user"]=details
			return redirect('/') # changes here
	return render_template("login.html")	
	#	return render_template('search.html',user=session["user"])


@app.route('/', methods=["POST","GET"])
def search():
	if "user" in session:
		user=session["user"]#db.execute("select * from user_login_details where id=:id", {"id":session['user'].id}).fetchone()
	else:
		user=[]
	if request.method== "POST":
			field = request.form.get("search_field")
			q=request.form.get("query")
			k=q.lower()
			pattern='%'+k+'%'
			if field=="isbn":
				
				matches=db.execute("select * from books where isbn like :pattern ",{"pattern":pattern})
				if matches.rowcount == 0:
	
					return render_template("search.html",user=user,q=q,sfield="isbn", message="No result found.")
				return render_template("search.html",user=user,q=q, sfield="isbn",matches=matches,rownum=matches.rowcount)

			if field=="title":
			
				matches=db.execute("select * from books where lower(title) like :pattern ",{"pattern":pattern})
				if matches.rowcount == 0:
	
					return render_template("search.html",user=user,q=q,sfield="title", message="No result found.")
				return render_template("search.html", user=user,q=q,sfield="title", matches=matches,rownum=matches.rowcount)

			if field=="author":
			
				matches=db.execute("select * from books where lower(author) like :pattern ",{"pattern":pattern})
				if matches.rowcount == 0:
	
					return render_template("search.html",user=user,q=q,sfield=field, message="No result found.")


				return render_template("search.html",user=user, q=q, sfield=field, matches=matches,rownum=matches.rowcount)
		
	return render_template("search.html", user=user)
	

@app.route('/search_by_isbn/<string:isbn>', methods=["GET","POST"])
def search_by_isbn(isbn):
	books=db.execute("select * from books where isbn=:isbn",{"isbn":isbn}).fetchone()
	#global user
	
	if books is None:
		return render_template("error.html",message="No book found.")
	
	if 'user' in session:
		user=session['user']
	else:
		user=[]
		
	if request.method=="POST":
		'''if 'user' in session:'''
		try:
			db.execute( "insert into reviews values( :isbn , :user_id,:rating, :review )",{"isbn":isbn, "user_id":session['user'].id, "rating":request.form.get("rating"),"review":request.form.get("review") })
			db.commit()
		except:
			return render_template("error.html",message="Already submitted")
		else:
			review=db.execute("SELECT * from reviews where isbn=:isbn and user_id=:user_id	",{"isbn":isbn,"user_id":session['user'].id}).fetchone()	
			return render_template('book.html',user=user,books=books,review=review)
			return render_template('book.html',user=user,books=books,success="Submitted.")
	if 'user' in session:		
		review=db.execute("SELECT * from reviews where isbn=:isbn and user_id=:user_id	",{"isbn":isbn,"user_id":session['user'].id}).fetchone()	
	else:
		review=[]
	try:
		res=requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":"prsUZ2NatVUJ26Otr5cgYQ","isbns":books.isbn})
		data=res.json()
	except:
		return render_template('book.html',user=user,books=books,review=review)
		return render_template('error.html',message="Unable to fetch requested data.")
	
	return render_template('book.html',user=user,books=books,data=data,review=review)

@app.route('/api/<string:isbn>')
def book_api(isbn):
	books=db.execute("select * from books where isbn=:isbn",{"isbn":isbn}).fetchone()
	if books is None:
		return jsonify({"error": "Invalid isbn"}), 404
	try:
		res=requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":"prsUZ2NatVUJ26Otr5cgYQ","isbns":books.isbn})
    
		data=res.json()
	except:
		return render_template('error.html',message="Unable to fetch requested data.")
		
	return jsonify({ "title":books.title,"author":books.author,"year":books.year,"isbn":books.isbn,"review_count":data['books'][0]['reviews_count'], "average_score": data['books'][0]['average_rating']  })
