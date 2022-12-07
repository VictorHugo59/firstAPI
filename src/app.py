from flask import Flask, jsonify, request, Response, render_template
from flask_pymongo import PyMongo
import pymongo
from bson import json_util
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app=Flask(__name__)
app.config['MONGO_URI']='mongodb://localhost/projectsdb'

mongo=PyMongo(app)

#welcome web page
@app.route('/',methods=['GET'])
def welcome():

    return render_template('index.html')

#visualize projects
@app.route('/projects',methods=['GET'])
def see_projects():
    projects=mongo.db.projects.find({},{'_id': False}) #bson
    
    response = json_util.dumps(projects)#json
    return Response(response, mimetype='application/json')

#create projects
#pass request as json: {"project1":"title1", "project2":"title2"} as many projects the user wants
@app.route('/create',methods=['POST'])
def create_project():
    count=0
    for project in request.json:
        count+=1
        title=request.json[project]
        title=title.replace(' ','')
        title=title.replace('#','_')
        date= datetime.datetime.now().strftime("%B %d %Y")
        date=date.replace(' ','_')
        if title and date:
            id = mongo.db.projects.insert_one(
                {'title': title, 'date_of_creation': date, 'updates':[]}) #insertamos a base de datos
        else:
            #podemos retornar nuestra funcion de error
            return {"message":"title not provided"}

    response={"message": str(count) + ' projects have been created'} #generamos la respuesta
    return response                

#delete one project
@app.route('/delete/<project>', methods=['DELETE'])
def delete_project(project):
    print(project)
    mongo.db.projects.delete_one({'title': project})
    message=jsonify({'message':project + ' has been succesfully deleted'})
    response=message
    return response

#delete ALL projects
@app.route('/delete_all', methods=['DELETE'])
def delete_all_projects():
    mongo.db.projects.drop()
    message=jsonify({'message':'All projects have been deleted'})
    return message

@app.route('/add_update/<project>',methods=['PUT'])
def update_project(project):
    count=0
    for update in request.json:
        count+=1
        title=request.json[update]
        title=title.replace(' ','_')
        mongo.db.projects.update_one({'title': project}, {'$push': {
            'updates':{title:[]}
        }},upsert=True)
    return {'message':'succesfully added '+ str(count)+' updates'}

@app.route('/add_update_description/<project>/<update>', methods=['PUT'])
def update_points(project,update):
    print(project,update)
    count=0
    for entries in request.json:
        count+=1
        entry=request.json[entries]
        mongo.db.projects.update_one({'title': project}, {'$push': {
            'updates.$[].{}'.format(update):{str(count):entry}
        }},upsert=False)

    return {'message': str(count)+' entries have been added to: '+ update}


@app.route('/search/date/<date>', methods=['GET'])
def search_date(date):
    array=json_util.dumps(mongo.db.projects.find({'date_of_creation':date},{'_id': False}))
    return array

@app.route('/search/name/<name>', methods=['GET'])
def search_name(name):
    array=json_util.dumps(mongo.db.projects.find({'title':name},{'_id': False}))
    return array

    

@app.errorhandler(404)
def not_found(error=None):
    response=jsonify({
        'message': 'Resource not found: '+ request.url,
        'status': 404
    })
    response.status_code=404
    return response

if __name__=="__main__":
    app.run()

