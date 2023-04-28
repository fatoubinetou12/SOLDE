from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm,entees, sortie
from flaskblog.models import User, Entrees,Depenses
from flask_login import login_user, current_user, logout_user, login_required
from flask import session
from decimal import Decimal



@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('transactions'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('transactions'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('transactions'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('transactions'))




@app.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
   
    form_entrees =  entees()
    form_sortie = sortie()
    entrees =Entrees.query.filter_by(author=current_user).all()
    depenses =Depenses.query.filter_by(autho=current_user).all()
    somme_entrees = sum([Decimal(e.montant_entrees) for e in entrees])
    somme_depenses = sum([Decimal(d.montant_depenses) for d in depenses])
    solde = somme_entrees - somme_depenses

    if form_entrees.submit_entees.data and form_entrees.validate():
        entre = Entrees(Libelle_entrees=form_entrees.libelle.data, montant_entrees=form_entrees.amount.data, author=current_user)
        db.session.add(entre)
        db.session.commit()
        flash('Entrée ajoutée avec succès', 'success')
        return redirect(url_for('transactions'))


    if form_sortie.submit_sortie.data and form_sortie.validate():
        
        depense = Depenses(Libelle_depenses=form_sortie.libelle.data, montant_depenses=form_sortie.amount.data, autho=current_user)
        if solde < form_sortie.amount.data:
             flash('Solde insuffisant', 'danger')
        else:
         db.session.add(depense)
         db.session.commit()
       
        
         flash('Dépense ajoutée avec succès', 'success')
        return redirect(url_for('transactions'))

 
    solde = somme_entrees - somme_depenses

   

    return render_template('transactions.html', form_entrees=form_entrees, form_sortie=form_sortie, solde=solde,entrees=entrees, depenses=depenses)



@app.route('/delete_entree/<int:id>')
@login_required
def delete_entree(id):
    entree = Entrees.query.get(id)
    db.session.delete(entree)
    db.session.commit()
    return redirect(url_for('transactions'))

@app.route('/delete_depenses/<int:id>')
def delete_depense(id):
    depenses = Depenses.query.get(id)
    db.session.delete(depenses)
    db.session.commit()
    return redirect(url_for('transactions'))
@app.route('/receipt')
@login_required
def receipt():
    user = current_user 
    entrees = Entrees.query.filter_by(author=user).all() 
    depenses = Depenses.query.filter_by(autho=user).all() 
    return render_template('receipt.html', user=user, entrees=entrees, depenses=depenses)





