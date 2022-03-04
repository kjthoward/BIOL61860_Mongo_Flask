from flask import render_template, redirect, url_for, request, flash, send_from_directory

from create_table import Var_Table
from flask_conf import app
from forms import SearchForm, AddNewVariantForm, ManualAddNewVariantForm
from helper import Database, Constants, Clean_Search, Clean_Form, Add_Variant
import random
import json
import os

db = Database()


# Route for the favicon (icon that is displayed in the tab)
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder,'favicon.ico')

# Main view, shows 10 random variants
@app.route("/")
def variants():
    cursor=db.find()
    total=db.estimated_document_count()
    section=random.randint(0,total-10)
    # section=total-10
    vars = [x for x in cursor[section:section+10]]
    vars_to_show=Var_Table(vars)
    return render_template('variants.html',data=vars_to_show, title=f"Random list of Variants ({section:,}-{section+10:,})")

# Search page, using the SearchForm
@app.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm()
    total=db.estimated_document_count()
    if form.cancel.data:
        return redirect(url_for('variants'))
    if form.validate():
        search_data=Clean_Form(form.data)
        return redirect(url_for('search_results', query=search_data))
    return render_template('search.html', form=form, total=f"{total:,}")
    
# Takes the query from SearchForm and makes a view of those results
@app.route("/search_results")
def search_results():
    query=eval(request.args["query"])
    query=Clean_Search(query)
    # import pdb; pdb.set_trace()
    cursor=db.find(query)
    vars = [x for x in cursor]
    if "mappings.assembly_name" in query.keys():
        vars_to_show=Var_Table(vars, assembly_spec=query["mappings.assembly_name"])
    else:
        vars_to_show=Var_Table(vars)
    if len(vars_to_show)==0:
        flash("Search returned no results")
        return redirect(url_for('search'))
    return render_template('variants.html',data=vars_to_show, title=f"Search Result")

# Page for adding new variants 
# NOTE - Manual doesn't work, will always give a fail message
@app.route("/add_new/<type>", methods=["POST", "GET"])
def add_new(type):
    if type =="API":
        form = AddNewVariantForm()
    elif type == "manual":
        form = ManualAddNewVariantForm()
    else:
        flash(f"Invalid argument: {type}")
        return redirect(url_for('variants'))
    total=db.estimated_document_count()
    if form.cancel.data:
        return redirect(url_for('variants'))
    if form.validate():
        if type=="API":
            identifier=Clean_Form(form.data)["name"]
            if len([x for x in db.find({"name":identifier})])!=0:
                flash(f"Data for {identifier} already exists")
                return redirect(url_for('search_results', query="{'name':'"+identifier+"'}"))
            added=Add_Variant(identifier)
        elif type=="manual":
            added=False
        if added==True:
            flash(f"Data for {identifier} added successfully")
            return redirect(url_for('search_results', query="{'name':'"+identifier+"'}"))
        else:
            flash(f"Unable to add {identifier}")
            return redirect(url_for('add_new',type=type))
    return render_template('add_new.html', form=form, total=f"{total:,}", type=type)
