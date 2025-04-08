from flask import Flask, render_template, request, redirect,session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy import select,ForeignKey



import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myproject.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.app_context().push()
db = SQLAlchemy(app)


class books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bookid = db.Column(db.String(50), nullable=False, unique=True)
    title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    publisher = db.Column(db.String(50), nullable=False)
    published_year = db.Column(db.Date, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status=db.Column(db.String(20),nullable=False)

    def __repr__(self):
        return f"{self.bookid},{self.title},{self.author},{self.publisher},{self.published_year},{self.price},{self.id}"


class students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usn = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.String(10), nullable=False)
    dept = db.Column(db.String(50), nullable=False)
    mobno = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"{self.id},{self.usn},{self.name}"
  
class reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usn = db.Column(db.String(50),ForeignKey(students.usn), nullable=False,)
    bookid = db.Column(db.String(50),ForeignKey(books.bookid),nullable=False)
    rdate= db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False)
       
    def __repr__(self):
        return f"{self.id},{self.usn},{self.bookid},{self.rdate},{self.status}"


@app.route('/cancelreservation/<bookid>,<rid>')
def cancelreservation(bookid,rid):
    
    #msg=f'recevid parameters are bookid = {bookid},reservation id {rid}'
    
    book=books.query.filter_by(bookid=bookid).first()
    book.status='available'
    db.session.commit()
    
    reser=reservation.query.get(rid)
    db.session.delete(reser)
    db.session.commit()
    
    return render_template('myreservations.html')

@app.route('/reserve/<int:id>,<bid>')
def reserver(id,bid):
    student_email=session.get("email")
    usn=session.get("usn")
    #msg=f"student email = {student_email},id = {id},usn={usn},bookid={bid}"
    rdate=datetime.date.today()
    res=reservation(usn=usn,bookid=bid,rdate=rdate,status='reserved')
    db.session.add(res)
    db.session.commit()
    
    book=books.query.filter_by(bookid=bid).first()
    book.status='reserved'
    db.session.commit()
    print(f'bookid = {bid} got updated')
    return redirect('/studenthomepage.html')


@app.route('/reservation.html',methods=['POST','GET'])
def reservations():
    
    if request.method=='POST':
        
        rdate=request.form['rdate']
        print(rdate)
        records=db.session.query(books,reservation,students).select_from(books).join(reservation).join(students).filter(reservation.rdate==rdate).all()
        return render_template('reservation.html',rows=records)
    else:
        return render_template('reservation.html')

@app.route('/myreservation.html')
def myreservation():
    usn=session.get("usn")
    #records=reservation.query.filter_by(usn=usn).all()
    
    # records=db.session.query(books,reservation).filter(reservation.usn==usn).join(reservation,books.bookid==reservation.bookid).first()
    
    
    records=db.session.query(books,reservation).join(reservation).filter(reservation.usn==usn).all()
    
    print('---------Result is---------')
    
    
    for row in records:
        print(row,type(row),end="*********")
    
    
    return render_template('myreservations.html',rows=records)
    
@app.route('/resetpwd.html',methods=['POST','GET'])
def resetpwd():
    
    if request.method=='POST':
        npwd=request.form['npwd']
        usn=session.get('usn')
        
        r=students.query.filter_by(usn=usn).first()
        r.password=npwd
        db.session.commit()
        return render_template('resetpwd.html',msg="done")
    else:
        return render_template('resetpwd.html')
    
@app.route('/studenthomepage.html')
def studenthomepage():
    
   
    #name=session.get('name')
    #print(f"Session name is : {name}")
    if session.get('name') is not None:
        
        res=db.session.query(books).all()
        
        
        # bookset=db.session.query(books,reservation).join(reservation,books.bookid!=reservation.bookid).all()
        #print(bkset,bookset,type(bkset),type(bookset))
        
        print(f"value of result = {res}")
        return render_template('studenthomepage.html',fn=session['name'],records=res)
    else:
        return "You must <a href='/'>Login</a> to continue"

@app.route('/logout.html')
def logout():
    session.pop('name',default=None)
    session.pop('email',default=None)
    session.pop('usn',default=None)
    
    return redirect('/')


@app.route('/updatebook.html', methods=['GET', 'POST'])
def updatebook():
    try:
        if request.method == 'POST':

            # for key in request.form.values():
            #     print(f"{key}")
            id = request.form['id']

            bookid = request.form['bookid']
            title = request.form['title']
            author = request.form['author']
            publisher = request.form['publisher']
            price = request.form['price']

            published_year = request.form['published_year']

            # "2000-12-22"

            year, month, day = [int(item)
                                for item in published_year.split('-')]
            py = datetime.datetime(year, month, day)

            print(py, type(py))

            b = db.session.query(books).get(id)
            b.bookid = bookid
            b.title = title
            b.author = author
            b.publisher = publisher
            b.published_year = py
            b.price = price
            db.session.commit()

            return redirect('/viewbooks.html')
        else:
            return render_template('newbook.html')
    except Exception as e:
        return render_template('edibook.html', msg=e)


@app.route('/delete_book/<int:id>')
def delete_book(id):
    rec = books.query.filter(books.id == id).delete()
    db.session.commit()
    return redirect('/viewbooks.html')


@app.route('/edit_book/<int:id>')
def edit_book(id):
    rec = db.session.query(books).get(id)
    print(rec, type(rec))
    print(rec.id)
    return render_template('editbook.html', book=rec)


@app.route('/viewbooks.html')
def viewbooks():
    bks = books.query.all()
    # print(bks)
    return render_template('viewbooks.html', rows=bks)


@app.route('/viewstudent.html')
def viewstudent():
    stds = students.query.all()
    # print(bks)
    return render_template('viewstudent.html', rows=stds)


@app.route('/home.html')
def home():
    return render_template('adminhomepage.html')


@app.route('/newbook.html', methods=['GET', 'POST'])
def newbook():
    try:
        if request.method == 'POST':

            # for key in request.form.values():
            #     print(f"{key}")

            bookid = request.form['bookid']
            title = request.form['title']
            author = request.form['author']
            publisher = request.form['publisher']
            price = request.form['price']

            published_year = request.form['published_year']

            # "2000-12-22"

            year, month, day = [int(item)
                                for item in published_year.split('-')]
            py = datetime.datetime(year, month, day)

            print(py, type(py))
            status="available"
            b = books(bookid=bookid, title=title, author=author,
                      publisher=publisher, published_year=py, price=price,status=status)
            db.session.add(b)
            db.session.commit()

            return render_template('newbook.html', msg="success")
        else:
            return render_template('newbook.html')
    except Exception as e:
        return render_template('newbook.html', msg=e)


@app.route('/newstudent.html', methods=['POST', 'GET'])
def newstudent():

    if request.method == 'POST':

        usn = request.form['usn']
        name = request.form['name']
        semester = request.form['semester']
        dept = request.form['dept']
        email = request.form['email']
        mobno = request.form['mobno']
        password = request.form['password']

        stu = students(usn=usn, name=name, semester=semester,
                       mobno=mobno, dept=dept, email=email, password=password)
        db.session.add(stu)
        db.session.commit()
        return render_template('newstudent.html', msg="success")
    else:
        return render_template('newstudent.html')


@app.route('/verifylogin', methods=['GET', 'POST'])
def verifylogin():
    if request.method == "POST":

        login_type = request.form['login_type']
        user_name = request.form['user_name']
        password = request.form['password']

        print(login_type, user_name, password)

        if login_type == "admin":

            if user_name.lower() == "admin" and password.lower() == "admin123":
                #return render_template('adminhomepage.html')
                return "1"
            else:
                # return render_template('index.html', msg="Login failed")
                return "0"
        elif login_type == "student":

            r = students.query.filter_by(
                email=user_name, password=password).first()
            if r == None:
                print("Login failed")
                return "0"
            else:
                print("Login is successfull")
                session['name'] = r.name
                session['email']=user_name
                session['usn'] = r.usn
                
                return "2"

    return "Done"


@app.route('/loadbooks')
def loadbooks():
    
    l=[]
    for item in range(1,10):
        l.append(item)
    
    print(l)
    return l
    

@app.route('/myprofile.html')    
def myprofile():
    
    usn=session.get('usn')
    r=students.query.filter_by(usn=usn).first()
    
    return render_template('myprofile.html',row=r)
    
@app.route('/')
def index():
    # py=datetime.datetime(2000,5,22)
    # b=books(bookid='B001',author='Balagurusamy',title='Let us c',publisher='BPB',published_year=py,price=560)
    # db.session.add(b)
    # db.session.commit()
    # print("Record got saved")
    
    # b=reservation.query.get(1)
    # db.session.delete(b)
    # db.session.commit()
    
    '''
    to delete all records of a table
    db.seesion.query(reservation).delete()
    db.seesion.commit()
    '''
    
    # records=books.query.all()
    
    # for rec in records:
    #     rec.status='available'
    
    # db.session.commit()
    
    
    session.pop('name',default=None)
    session.pop('email',default=None)
    
    # stmt = select(books,reservation).join(books.bookid).order_by(books.id)

    
    # for row in db.session.execute(stmt):
    #     print(f"{row.books.title} {row.reservation.status}")
    
    # res=db.session.query(books,reservation).join(reservation,books.bookid==reservation.bookid).all()
    
    # for row in res:
    #     print(res)
    
    result=db.session.query(books,reservation).join(reservation).filter(reservation.usn=='4UB20CS001').first()
    i=0
    for row in result:
        
       #print(row,type(row))
       
       if isinstance(row,books):
           print(row.title,end=",")
       elif isinstance(row,reservation):
           print(row.usn)
    #    for item in row:
    #        print(type(item),end='*')
       
    return render_template('index.html')


if __name__ == '__main__':
    db.create_all()
    #db.drop_all()
    
    #print("Tables got dropped")
    
    app.run(debug=True,host="0.0.0.0")
