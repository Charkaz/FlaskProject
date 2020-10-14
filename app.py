from flask import Flask,render_template,redirect,request,url_for,jsonify,flash
from flask_sqlalchemy import SQLAlchemy
import os
import time
from datetime import date,datetime
import random
from calendar import monthrange
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = 'alishancharkaz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'data.sqlite')
db = SQLAlchemy(app)



class isciler(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    adsoyad = db.Column(db.String(50),unique=True)
    status  = db.Column(db.Boolean)
    maas    = db.Column(db.Float)
    hesab   = db.Column(db.Float)
    qrup    = db.Column(db.String(50))
    ayliq   = db.Column(db.Boolean)
    qeydtarix = db.Column(db.DateTime)
  


class proces(db.Model):
    id      = db.Column(db.Integer,primary_key = True)
    adsoyad = db.Column(db.String(50))
    baslama = db.Column(db.DateTime)
    bitme   = db.Column(db.DateTime)
    mebleg  = db.Column(db.Float)
    qrup    = db.Column(db.String(50))
    status  = db.Column(db.Boolean)
    veziyyet = db.Column(db.Boolean)

class qrup(db.Model):
    id     = db.Column(db.Integer,primary_key = True)
    qrupad = db.Column(db.String(50))


class odeme(db.Model):
    id    = db.Column(db.Integer,primary_key = True)
    adsoyad = db.Column(db.String(50))
    miqdari = db.Column(db.Float)
    tarix = db.Column(db.DateTime)


@app.route("/")
def index():
    axtar = request.form.get("axtar")
    iscilerim = isciler.query.filter_by(ayliq = False)
    qruplarim = qrup.query.filter_by()
    return render_template("index.html",iscilerim = iscilerim,qruplarim = qruplarim)


@app.route("/",methods=["POST"])
def index2():
    axtar = request.form.get("axtar")
    search = "%{}%".format(axtar)
    iscilerim = isciler.query.filter(isciler.adsoyad.like(search),isciler.ayliq == False).all()
    qruplarim = qrup.query.filter_by()
    return render_template("index.html",iscilerim = iscilerim,qruplarim = qruplarim)


@app.route("/yekun",methods =["POST"])
def yoxla():
    ad = request.form["ad"]
    ad = ad.split("|")
    tarixim = request.form.get("tarix")
    #------------------------
    year = tarixim[:4]
    month = tarixim[5:7]
    day = tarixim[8:10]
    hour = tarixim[11:13]
    second = tarixim[14:16]
    trx = None
    if year and month and day and hour and second:    
        trx = datetime(int(year),int(month),int(day),int(hour),int(second))
        print(trx)
    else:
        print("tarix sehfdir")
   #-------------------------
    if trx:
        for i in range(0,len(ad)-1):
            iscim = isciler.query.filter_by(adsoyad = ad[i]).first()
            prom = proces.query.filter_by(adsoyad = iscim.adsoyad,bitme = None).first()
            prom.bitme = trx
            yekuntarix = str(prom.bitme - prom.baslama)
            if not("day" in yekuntarix):
                prom.veziyyet = False
                iscim.status = False
                ykn = yekuntarix.split(":")
                saat = int(ykn[0]) + float(int(ykn[1])/60)
                prom.mebleg = iscim.maas * saat
                iscim.hesab = round(iscim.hesab + (saat * iscim.maas),1)
                flash("prosesler ugurla yekunlasdirildi!","success")
            else:
                prom.bitme = None
                flash("24 saatdan cox is mumkun deyil!","warning")
        db.session.commit()
    else:
        flash("tarixle bagli problem ola biler","danger")
    return jsonify("good")


@app.route("/yukle",methods =["POST"])
def yukle():
    ad = request.form["ad"]
    qrupad = request.form["qrup"]
    tarixim = request.form.get("tarix")
    #------------------------
    year = tarixim[:4]
    month = tarixim[5:7]
    day = tarixim[8:10]
    hour = tarixim[11:13]
    second = tarixim[14:16]
    trx = None
    if year and month and day and hour and second:    
        trx = datetime(int(year),int(month),int(day),int(hour),int(second))
        print(trx)
    else:
        print("tarix sehfdir")
   #-------------------------
    ad = ad.split("|")
    proseslerim = proces.query.filter_by(veziyyet = True,qrup = qrupad)
    aktivadsoyad= [i.adsoyad for i in proseslerim] 
    if trx:
        for i in range(0,len(ad)-1):
    
            iscim = isciler.query.filter_by(adsoyad = ad[i]).first()
            if iscim.adsoyad in aktivadsoyad:
                print(iscim.adsoyad,aktivadsoyad)
            else:
                if iscim.status == False :
                    iscim.status = True
                    iscim.qrup = qrupad
                    newProces = proces(adsoyad = iscim.adsoyad,qrup = iscim.qrup,status=False,baslama = trx ,veziyyet = True)
                    db.session.add(newProces)
                    flash("proces ugurla basladildi","success")
                else:
                    prom = proces.query.filter_by(adsoyad = iscim.adsoyad,bitme = None).first()
                    prom.bitme = trx
                    prom.veziyyet = False

                    yekuntarix = str(prom.bitme - prom.baslama)
                    if not("day" in yekuntarix):
                        ykn = yekuntarix.split(":")
                        saat = int(ykn[0]) + float(int(ykn[1])/60)
                        prom.mebleg = iscim.maas * saat
                        iscim.hesab =round(iscim.hesab + (saat * iscim.maas),1)
                        iscim.status = True
                        iscim.qrup = qrupad
                        newProces = proces(adsoyad = iscim.adsoyad,qrup = iscim.qrup,baslama = trx,status=True,veziyyet = True)
                        db.session.add(newProces)
                        flash("proces ugurla deyisdirildi","success")
                    else:
                        prom.bitme = None
                        flash("Bir isden digerine kecdikde saatin 1 gunden cox olamasina diqqet edin","primary")
        db.session.commit()
    else:
        flash("zehmet olmasa tarixi duz secin!","danger")
    return jsonify("process ugurludur!")

@app.route("/isciqeyd",methods = ["POST"])
def isciqeyd():
    adsoyad = request.form.get("adsoyad")
    maas = request.form.get("maas")
    if float(maas) < 20:
        if adsoyad and maas:
            newIsci = isciler(adsoyad = adsoyad,maas=maas,ayliq = False,status = False,hesab = 0.0,qrup = "",qeydtarix = datetime.now())
            db.session.add(newIsci)
            db.session.commit()
            flash("Qeydiyyat ugurla basa catdi","success")
            return redirect(url_for("index"))
    else:
        if adsoyad and maas:
            curretnt_date = datetime.now()
            lazim = datetime(curretnt_date.year,curretnt_date.month,curretnt_date.day) 
            newIsci = isciler(adsoyad = adsoyad,maas=maas,ayliq = True,status = False,hesab = 0.0,qrup = "",qeydtarix = lazim)
            
            # buraya sonra baxmali 
            db.session.add(newIsci)
            db.session.commit()
            flash("Qeydiyyat ugurla basa catdi","success")
        return redirect(url_for("index"))



def ayliqIsciler():
    curretnt_date = datetime.now()
    lazim = datetime(curretnt_date.year,curretnt_date.month,curretnt_date.day) 
    ayliqIsciler = isciler.query.filter(isciler.ayliq == True, isciler.qeydtarix < lazim).all()
    aydagun = monthrange(lazim.year,lazim.month)[1] 
    
    for isci  in ayliqIsciler:
        if aydagun == 31:
            esas = (isci.maas/31)
            isci.hesab += esas
            isci.qeydtarix = lazim
        elif aydagun == 30:
            esas = (isci.maas/30)
            isci.hesab += esas
            isci.qeydtarix = lazim
        elif aydagun == 28:
            esas = (isci.maas/28)
            isci.hesab += esas
            isci.qeydtarix = lazim
        elif aydagun == 29:
            esas = (isci.maas/29)
            isci.hesab += esas
            isci.qeydtarix = lazim


    db.session.commit()
    return True




@app.route("/odenecekler")
def odenileceklerim():
    tarix = datetime.now()
    iscilerim = isciler.query.filter(isciler.hesab > 0 )
    toplam = 0
    for i in iscilerim:
        toplam += i.hesab
    return render_template("faktura2.html",tarix= tarix,iscilerim = iscilerim,toplam = toplam)

@app.route("/iscilerim")
def iscilerim():
    iscilerim = isciler.query.filter_by()
    return render_template("isciler.html",iscilerim = iscilerim)


@app.route("/iscilerim",methods = ["POST"])
def iscilerimaxtar():
    axtar = request.form.get("axtar")
    sorgu = "%{}%".format(axtar)
    iscilerim = isciler.query.filter(isciler.adsoyad.like(sorgu))
    return render_template("isciler.html",iscilerim = iscilerim)

@app.route("/delete/<string:id>")
def delete(id):
    iscim = isciler.query.filter_by(id = id).first()
    db.session.delete(iscim)
    db.session.commit()
    return redirect(url_for("iscilerim"))
@app.route("/update/<string:id>")
def isciupdate(id):
    iscim = isciler.query.filter_by(id = id).first()

    return render_template("isciupdate.html",iscim = iscim)

@app.route("/updateisci/<string:id>",methods = ["POST"])
def updateteisci(id):
    iscim = isciler.query.filter_by(id = id).first()
    adsoyad = request.form.get("adsoyad")
    maas = request.form.get("maas")
    iscim.adsoyad = adsoyad
    iscim.maas = maas
    db.session.commit()
    return redirect(url_for("iscilerim"))

@app.route("/jurnal")
def jurnal():
    aktivpro = proces.query.filter_by(veziyyet = True)
    passivpro = proces.query.filter_by(veziyyet = False).order_by(proces.bitme.desc())
    return render_template("jurnal.html",aktivpro = aktivpro,passivpro = passivpro)

@app.route("/jurnal",methods = ["POST"])
def jurnalaxtar():
    axtar = request.form.get("axtar")
    sorgu = "%{}%".format(axtar)
    aktivpro = proces.query.filter(proces.adsoyad.like(sorgu),proces.veziyyet == True)
    passivpro = proces.query.filter(proces.adsoyad.like(sorgu),proces.veziyyet == False).order_by(proces.bitme.desc())
    return render_template("jurnal.html",aktivpro = aktivpro,passivpro = passivpro)

@app.route("/odenis/<string:id>")
def odenis(id):
    iscim = isciler.query.filter_by(id = id).first()

    return render_template("odenis.html",iscim = iscim)

@app.route("/odeniset/<string:id>",methods = ["POST"])
def odeniset(id):
    try:
        iscim = isciler.query.filter_by(id = id).first()
        miqdarim = float(request.form.get("miqdar"))
        odenisim = odeme(miqdari = miqdarim ,adsoyad = iscim.adsoyad, tarix = datetime.now())
        iscim.hesab = iscim.hesab - miqdarim
        db.session.add(odenisim)
        db.session.commit()
        flash("Odenis ugurla aparildi ." ,"success")
        return redirect(url_for("iscilerim"))
    except:
        flash("zehmet olmasa odenilen miqdarin herf tipinde olmamasina diqqet edin!","danger")
        return redirect("/odenis/"+id)

@app.route("/odenisler")
def odenisler():
    odenislerim = odeme.query.filter_by()
    return render_template("odenisler.html",odenislerim = odenislerim)

@app.route("/odenisler",methods = ["POST"])
def odenisleraxtar():
    axtar = request.form.get("axtar")
    sorgu = "%{}%".format(axtar)
    odenislerim = odeme.query.filter(odeme.adsoyad.like(sorgu))
    return render_template("odenisler.html",odenislerim = odenislerim)


if __name__ == "__main__":
    db.create_all()
    print(ayliqIsciler())
    app.run(debug=True,host ='localhost' ,port= 5000)
