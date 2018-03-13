###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, ValidationError, RadioField# Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, Length# Here, too
from flask_sqlalchemy import SQLAlchemy
import requests
import json


## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True

## All app.config values
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364'

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/SI364midterm"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)




######################################
######## HELPER FXNS (If any) ########
######################################


    


##################
##### MODELS #####
##################


class IngredientSearched(db.Model):
     __tablename__ = "ingresearch"
     id = db.Column(db.Integer,primary_key=True)
     ingredientssearch = db.Column(db.String(250))
     reciepe_id = db.relationship('Reciepes',backref='IngredientSearched')
    
     def __repr__(self):
        return "{} (ID: {})".format(self.ingredientssearch, self.id)

class Reciepes(db.Model):
    __tablename__ = "reciepes"
    id = db.Column(db.Integer,primary_key=True)
    search_id = db.Column(db.Integer,db.ForeignKey("ingresearch.id"))
    reciepe = db.Column(db.String(250))
    link = db.Column(db.String(250))
    ingredients = db.Column(db.String(250))
    
    def __repr__(self):
        return "{} (ID: {})".format(self.reciepe, self.id)
    
    



###################
###### FORMS ######
###################

def validatesearch(self, field):
    words = field.data.split()
    if len(words) > 1:
        for x in words[:-1]:
            if x[-1] != ",":
        
                raise ValidationError("Ingredients must be separated with commas")
                #custom validation to make sure words are separated with a comma


class ReciepeForm1(FlaskForm):
    search = StringField("Search reciepes by entering ingredients", validators=[Required(),Length(1,250), validatesearch])
    submit = SubmitField()
    
class ReciepeForm(FlaskForm):
    search = StringField("Find reciepes with ingredients you have already searched", validators=[Required(),Length(1,250), validatesearch])
    number = RadioField("How many reciepes do you want?", choices = [('1','1'), ('2','2'),('3','3'),('4','4'),('5','5')], validators=[Required()])
    submit = SubmitField()
    




#######################
###### VIEW FXNS ######
#######################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def home():
  
    return render_template('base.html')
    
@app.route('/reciepeform1', methods=["GET","POST"])
def reciepe_form1():
    form = ReciepeForm1() #GET form
    if form.validate_on_submit():
        
        return redirect(url_for('displayData'))
    
     
    return render_template('reciepeform1.html', form = form)
           

    

@app.route('/result', methods = ['POST', 'GET'])
def displayData():
    form = ReciepeForm1()
    if request.args:
        ingredients = request.args['search']
    
    
        baseurl = "http://www.recipepuppy.com/api/"
        params = {"i": ingredients}
        r = requests.get(baseurl, params = params)
        data = r.json()
    
        new_search = IngredientSearched.query.filter_by(ingredientssearch = ingredients).first() #checks if exists in database first
        if not new_search:
    
            new_search = IngredientSearched(ingredientssearch = ingredients)
            db.session.add(new_search)
            db.session.commit()
        
    
        for x in data['results']:
            new_reciepe = Reciepes(reciepe = x['title'], link = x['href'], ingredients =              x['ingredients'], search_id = new_search.id )
            db.session.add(new_reciepe)
            db.session.commit()
            
        results = data['results']
         
        if results:
     
            return render_template('results1.html', results = results)
        
        else:
            nothing = True 
        
            return render_template('reciepeform1.html', form = form, nothing = nothing)
     
    return redirect(url_for('reciepe_form1'))


@app.route('/reciepeform2', methods=["GET","POST"])
def reciepe_form2():
    form = ReciepeForm()
    if form.validate_on_submit():
           
        ingredients = form.search.data
        num = int(form.number.data)
            
        q = IngredientSearched.query.filter_by(ingredientssearch=ingredients).first()
        re = []
            
        if q:
                
             results = Reciepes.query.filter_by(search_id = q.id).all()
                
             for x in results[:num]:
                  re.append((x.reciepe, x.ingredients, x.link))
            
             return render_template('reciepeform2.html',form = form, results = re)
            
        else:
            nothing = True
                
            return render_template('reciepeform2.html', form = form, nothing = nothing)   
        
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))        
         
                        
    return render_template('reciepeform2.html',form = form)
    
@app.route('/allsearches', methods=["GET","POST"])
def all_searches():
    Ingredientssearched = IngredientSearched.query.all()
    return render_template('allsearches.html', Ingredientssearched = Ingredientssearched)
 

@app.route('/reciepe/<ingredient>')
def recipes(ingredient):
    baseurl = "http://www.recipepuppy.com/api/"
    params = {"i": ingredient}
    r = requests.get(baseurl, params = params)
    re = r.json()
    results = re['results']
    return render_template('dynamic.html', results = results)

## Code to run the application...

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
if __name__ == '__main__':
    db.create_all()     
    app.run(use_reloader=True,debug=True) 