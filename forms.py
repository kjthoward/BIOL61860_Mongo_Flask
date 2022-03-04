from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DecimalField, SelectField
from wtforms.validators import InputRequired
from helper import Constants
import re

class SearchForm(FlaskForm):
    name = StringField('Identifier',render_kw={"placeholder": "e.g. rs772176415"})
    assembly = SelectField(label="Assembly", validators=[InputRequired()], choices=[(k,v) for k,v in Constants["assembly"].items()], default=2, coerce=int)
    chr = SelectField('Chromosome', choices=[("", "---")]+[(val,f"Chr{val}") for val in range(1,23)] + [("X", "ChrX"), ("Y", "ChrY")])
    start = IntegerField('Start', render_kw={"placeholder": "e.g. 23605469"})
    end = IntegerField('End', render_kw={"placeholder": "e.g. 23605500"})
    search = SubmitField('Search')
    cancel = SubmitField('Cancel')

    def validate(self):
        if self.data["search"]==True:
            def is_blank(field):
                if field is None:
                    return True
                else:
                    return False
            if any([is_blank(self.data["start"]), 
                    is_blank(self.data["end"])]):
                if not all([is_blank(self.data["start"]), is_blank(self.data["end"])]):
                    if is_blank(self.data["start"]):
                        self.start.errors = (("If Start or End is used they must both contain values"),)
                    if is_blank(self.data["end"]):
                        self.end.errors = (("If Start or End is used they must both contain values"),)#
                else:
                    return True
            elif self.data["end"]<self.data["start"]:
                self.start.errors = (("Start location must be greater than End location"),)
            else:
                return True

class AddNewVariantForm(FlaskForm):
    name = StringField('dbSNP ID', render_kw={"placeholder": "e.g. rs772176415"})
    search = SubmitField('Pull From dbSNP')
    cancel = SubmitField('Cancel')
    
    def validate(self):
        regex = "(rs)[1-9]+"
        if self.data["search"]==True:
            if self.data["name"]=="":
                self.name.errors = (("dbSNP ID must be entered"),)
            elif bool(re.match(regex, self.data["name"]))==False:
                self.name.errors = (("dbSNP ID is not in the correct format. It must be 'rs' followed by one or more numbers"),)
            else:
                return True
                
class ManualAddNewVariantForm(FlaskForm):
    name = StringField('Identifier', render_kw={"placeholder": "e.g. rs772176415"})
    assembly = SelectField(label="Assembly", validators=[InputRequired()], choices=[(k,v) for k,v in Constants["assembly"].items()], default=2, coerce=int)
    chr = SelectField('Chromosome', choices=[(val,f"Chr{val}") for val in range(1,23)] + [("X", "ChrX"), ("Y", "ChrY")])
    start = IntegerField('Start', validators=[InputRequired()], render_kw={"placeholder": "e.g. 23605469"})
    end = IntegerField('End', validators=[InputRequired()], render_kw={"placeholder": "e.g. 23605500"})
    maf = DecimalField('Maf', render_kw={"placeholder": "e.g. 0.0000052"})
    ref = StringField('Reference DNA Base', validators=[InputRequired()], render_kw={"placeholder": "e.g. A"})
    alt = StringField('Alternate DNA Base', validators=[InputRequired()], render_kw={"placeholder": "e.g. T"})
    consequence = StringField('Consequence', validators=[InputRequired()], render_kw={"placeholder": "e.g. missense_variant"})
    clincal = StringField('Clincal Significance', validators=[InputRequired()], render_kw={"placeholder": "e.g. likely pathogenic"})
    cdna = StringField('HGVSc Nomenclature', validators=[InputRequired()], render_kw={"placeholder": "e.g. NM_024675.3:c.688G>T"})
    submit = SubmitField('Submit Variant')
    cancel = SubmitField('Cancel')
    def validate(self):
        if self.data["submit"]==True:
            if self.data["end"]<self.data["start"]:
                self.start.errors = (("Start location must be greater than End location"),)
            else:
                return True
