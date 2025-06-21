import base64
import json
import random
from urllib import request

from django.http import JsonResponse
from django.shortcuts import render,HttpResponse
from index.database_design.database import *
from index.database_design.users import *
from django.http import JsonResponse
import base64

class Database_connection:
    def __init__(self):
        self.connection = None
        self.pwd=None
        self.userid=None
        self.role=None
    def connect(self,conn,pwd,userid,role):
        self.connection=conn
        self.pwd=pwd
        self.userid=userid
        self.role=role

    def close_connection(self):
        self.connection.close()

    def relink(self):
        self.connection=open_connection(self.userid,self.pwd)


conn=Database_connection()
# Create your views here.
def login(request):
    if request.method == 'GET':
        return render(request, 'check.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 进行账号密码验证，这里假设使用简单的验证方式，实际中应该使用更安全的验证方式，比如Django自带的用户认证系统
        role = request.POST.get('role')  # 获取角色参数

        if role=="auditor" and username[0]!='A':
            return JsonResponse({'status': 'fail'})  # 验证失败
        if role=='ruser' and len(username) !=10:
            return JsonResponse({'status': 'fail'})  # 验证失败
        elif role=='company' and len(username)!=7:
            return JsonResponse({'status': 'fail'})  # 验证失败
        elif role=='hr' and (len(username)!=8 or username[0]=='A'):
            return JsonResponse({'status': 'fail'})

        conn.connect(open_connection(username, password),password,username,role)

        if not conn.connection:
            return JsonResponse({'status': 'fail'})  # 验证失败
        else:
            return JsonResponse({'status': 'success'})


def ur(request):
    resumes=[]
    if request.method == 'GET':
        sql = 'select photo,userid,telephone,Raddress,highestEdu,experience,age,name,sex from Ruser where userid=%s'
        result = select_with_para(conn.connection, sql, (str(conn.userid)))
        if result[0]['photo']:
            binary_image_data = result[0]['photo']
            # 将二进制图片数据转换为base64编码字符串
            base64_image_data = base64.b64encode(binary_image_data).decode('utf-8')
        else:
            base64_image_data = ''
        sql='select * from resume where userid=%s'

        resume = select_with_para(conn.connection, sql, (str(conn.userid)))
        resumes = [i['resumeid'] for i in resume]
        sql='select schoolname,schoolLogo,schooltype,degree,major,finishdate from [dbo].[college_education_experience],school where userid=%s and [college_education_experience].schoolid=school.schoolid'
        education_experience = select_with_para(conn.connection, sql, (str(conn.userid)))
        if len(education_experience) != 0:
            for ee in education_experience:
                ee['schoolLogo']=shift_image(ee['schoolLogo'])
                ee['finishdate']=str(ee['finishdate'])

        sql='select * from school'
        school = select(conn.connection,sql)
        for ss in school:
            ss['schoolLogo']=shift_image(ss['schoolLogo'])
            ss['schoolname']=ss['schoolname'].rstrip()
        # 传递base64编码的图片数据给模板
        return render(request, 'role/ur.html', {'image_data': base64_image_data,
                                                 'userid': result[0]['userid'],
                                                 'telephone': result[0]['telephone'],
                                                 'Raddress': result[0]['Raddress'],
                                                 'highestEdu': result[0]['highestEdu'],
                                                 'experience': result[0]['experience'],
                                                 'age': result[0]['age'],
                                                 'name': result[0]['name'],
                                                 'sex': result[0]['sex'],'resume':[re['advantages'].rstrip() for re in resume],
                                                'lengths':len([re['advantages'] for re in resume]),
                                                'education_experience':education_experience,
                                                'lengths_of_education_experience':len(education_experience),
                                                'school':school},

                      )

    elif request.method == 'POST':
        body_data = request.body

        # 将字节字符串解码为字符串
        body_text = body_data.decode('utf-8')

        # 将字符串解析为JSON对象
        json_data = json.loads(body_text)
        label=json_data.get('label')
        if label=='data':

            userid = json_data.get('userId')
            telephone = json_data.get('phone')
            Raddress = json_data.get('location')
            highestEdu = json_data.get('education')
            experience = json_data.get('experience')
            age = json_data.get('age')
            name = json_data.get('name')
            sex = json_data.get('gender')
            print(telephone, Raddress, highestEdu, experience, age, name, sex, userid)

            sql = 'update Ruser set telephone=%s, Raddress=%s, highestEdu=%s, experience=%s, age=%s, name=%s,sex=%s where userid=%s'
            try:
                insert(conn.connection, sql, (telephone, Raddress.encode('cp936'), highestEdu.encode('cp936'), experience.encode('cp936'), age, name.encode('cp936'), sex.encode('cp936'), userid))
                return JsonResponse({'message': 'User information updated successfully'})
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': 'Failed to update user information'}, status=400)

        elif label=='changePassword':
            current_password = json_data.get('currentPassword')
            new_password = json_data.get('newPassword')

            # 检查当前密码是否正确
            if current_password != conn.pwd:
                return JsonResponse({'error': '当前密码不正确，请重试'}, status=400)

            # 如果一切正常，更新密码并返回成功消息
            conn.pwd=new_password
            saconn=sa_connection()

            try:
                conn.close_connection()
                execute(saconn,'delete_user',(conn.userid,))
                execute(saconn,'create_user',(conn.userid,new_password,'U'))
                saconn.close()
                conn.relink()
                return JsonResponse({'message': '密码修改成功！'}, status=200)
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': '后台报错'}, status=400)
        elif label=='edu':
            schoolid=json_data.get('schoolid')
            degree=json_data.get('degree')
            major=json_data.get('major')
            graduationYear=json_data.get('graduationYear')

            try:
                sql = 'insert into [dbo].[college_education_experience] values(%s,%s,%s,%s,%s)'
                insert(conn.connection,sql,(conn.userid,schoolid,degree.encode('cp936'),major.encode('cp936'),graduationYear))
                response_data = {'message': '简历保存成功！'}
                return JsonResponse(response_data)
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': 'Failed to update user information'}, status=400)

        elif label=='del':
            schoolid=json_data.get('schoolid')
            degree=json_data.get('degree')
            print(schoolid,degree)
            try:
                sql = 'delete from [dbo].[college_education_experience] where userid=%s and degree=%s and schoolid=%s'
                delete(conn.connection,sql,(conn.userid,degree.encode('cp936'),schoolid))
                response_data = {'message': '简历保存成功！'}
                return JsonResponse(response_data)
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': 'Failed to update user information'}, status=400)
        elif label == 'photo':
            photo=json_data.get('image_data')
            photo=base64.b64decode(photo)

            try:
                sql='update ruser set photo=%s where userid=%s'
                update(conn.connection,sql,(photo,conn.userid))
                return JsonResponse({'message': '密码修改成功！'}, status=200)
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': '后台报错'}, status=400)


        else:
            resume1 = json_data.get('resume1')
            resume2 = json_data.get('resume2')
            resume3 = json_data.get('resume3')
            resume_content=[resume1,resume2,resume3]

            # 在这里执行保存简历的操作，可以是将简历内容存入数据库或文件中
            try:
                sql = 'select * from resume where userid=%s'

                resume = select_with_para(conn.connection, sql, (str(conn.userid)))
                resumes = [i['resumeid'] for i in resume]
                if len(resume_content) != 0:
                    for idx, resumid in enumerate(resumes):
                        sql = 'update resume set advantages=%s where resumeid=%s'
                        update(conn.connection, sql, (resume_content[idx].encode('cp936'), resumid))

                if len(resumes) < len(resume_content):
                    count = len(resume_content) - len(resumes)
                    for i in range(count):
                        sql = 'insert into resume(resumeid,advantages,userid) values(%s,%s,%s)'
                        resumeid = "{:05}".format(random.randint(0, 99999)) + "{:08}".format(
                            random.randint(0, 99999999))
                        insert(conn.connection, sql, (resumeid, resume_content[len(resumes) + i].encode('cp936'), conn.userid))
                # 响应保存结果
                response_data = {'message': '简历保存成功！'}
                return JsonResponse(response_data)
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': 'Failed to update user information'}, status=400)

def ue(request):
    if request.method == 'GET':
        sql = 'select enterpriselogo as photo,enterpriseid as userid,enterpriseaddress as Raddress,enterprisename as name,type1,type2,introduction,city.cityname from enterprise,city where enterpriseid=%s and (enterprise.cityid=city.cityid or enterprise.cityid is null)'
        result = select_with_para(conn.connection, sql, (str(conn.userid)))
        if result[0]['photo']:
            binary_image_data = result[0]['photo']
            # 将二进制图片数据转换为base64编码字符串
            base64_image_data = base64.b64encode(binary_image_data).decode('utf-8')
        else:
            base64_image_data = ''
        sql = 'select * from resume where userid=%s'

        resume = select_with_para(conn.connection, sql, (str(conn.userid)))
        resumes = [i['resumeid'] for i in resume]
        sql='select hrid from hruser where enterpriseid=%s'
        hrs=select_with_para(conn.connection, sql, (str(conn.userid)))
        sql='select cityname from city'
        city = select(conn.connection, sql)
        # 传递base64编码的图片数据给模板
        return render(request, 'role/ue.html', {'image_data': base64_image_data,
                                                'userid': result[0]['userid'],
                                                'Raddress': result[0]['Raddress'],
                                                'name': result[0]['name'],
                                                'introduction': result[0]['introduction'].rstrip(),
                                                'city': result[0]['cityname'],
                                                'type1': result[0]['type1'],
                                                'type2': result[0]['type2'],
                                                'hrs':hrs,
                                                'cities':city
                                                }, )

    elif request.method == 'POST':
        body_data = request.body

        # 将字节字符串解码为字符串
        body_text = body_data.decode('utf-8')

        # 将字符串解析为JSON对象
        json_data = json.loads(body_text)
        label = json_data.get('label')
        if label == 'data':

            userid = json_data.get('userId')
            Raddress = json_data.get('location')
            name = json_data.get('name')
            introduction = json_data.get('Introduction')
            city = json_data.get('city')
            type1 = json_data.get('Type1')
            type2 = json_data.get('Type2')
            print(city)
            sql = 'select cityid from city where cityname=%s'
            city_id = select_with_para(conn.connection, sql, (city.rstrip()).encode('cp936'))
            print(city,city_id)
            city_id=city_id[0]['cityid']
            sql = 'update enterprise set enterpriseaddress=%s,enterprisename=%s,introduction=%s,cityid=%s,type1=%s,type2=%s where enterpriseid=%s'
            try:
                insert(conn.connection, sql, (
                    Raddress.encode('cp936'), name.encode('cp936'), introduction.encode('cp936'), city_id, type1.encode('cp936'), type2.encode('cp936'),userid))
                return JsonResponse({'message': 'User information updated successfully'})
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': 'Failed to update user information'}, status=400)

        elif label == 'changePassword':
            current_password = json_data.get('currentPassword')
            new_password = json_data.get('newPassword')

            # 检查当前密码是否正确
            if current_password != conn.pwd:
                return JsonResponse({'error': '当前密码不正确，请重试'}, status=400)

            # 如果一切正常，更新密码并返回成功消息
            conn.pwd = new_password
            saconn = sa_connection()

            try:
                conn.close_connection()
                execute(saconn, 'delete_user', (conn.userid,))
                execute(saconn, 'create_user', (conn.userid, new_password, 'U'))
                saconn.close()
                conn.relink()
                return JsonResponse({'message': '密码修改成功！'}, status=200)
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': '后台报错'}, status=400)
        elif label == 'photo':
            photo=json_data.get('image_data')
            photo=base64.b64decode(photo)

            try:
                sql='update enterprise set enterpriseLogo=%s where enterpriseid=%s'
                update(conn.connection,sql,(photo,conn.userid))
                return JsonResponse({'message': '密码修改成功！'}, status=200)
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': '后台报错'}, status=400)




def ua(request):
    if request.method == 'GET':
        sql = 'select photo,auditorid as userid,age,auditorname as name,sex,audit_num,audit_num_monthly from auditor where auditorid=%s'
        result = select_with_para(conn.connection, sql, (str(conn.userid)))
        if result[0]['photo']:
            binary_image_data = result[0]['photo']
            # 将二进制图片数据转换为base64编码字符串
            base64_image_data = base64.b64encode(binary_image_data).decode('utf-8')
        else:
            base64_image_data = ''

        # 传递base64编码的图片数据给模板
        return render(request, 'role/ua.html', {'image_data': base64_image_data,
                                                'userid': result[0]['userid'],
                                                'age': result[0]['age'],
                                                'name': result[0]['name'],
                                                'sex': result[0]['sex'],
                                                'audit_num': result[0]['audit_num'],
                                                'audit_num_monthly': result[0]['audit_num_monthly']}, )

    elif request.method == 'POST':
        body_data = request.body

        # 将字节字符串解码为字符串
        body_text = body_data.decode('utf-8')

        # 将字符串解析为JSON对象
        json_data = json.loads(body_text)
        label = json_data.get('label')
        if label == 'data':

            userid = json_data.get('userId')
            age = json_data.get('age')
            name = json_data.get('name')
            sex = json_data.get('gender')
            audit_num = json_data.get('audit_num')
            audit_num_monthly = json_data.get('audit_num_monthly')


            sql = 'update auditor set age=%s, auditorname=%s,sex=%s,audit_num=%d,audit_num_monthly=%d where auditorid=%s'
            try:
                insert(conn.connection, sql, (
                age,name.encode('cp936'),sex.encode('cp936'),audit_num,audit_num_monthly,userid))
                return JsonResponse({'message': 'User information updated successfully'})
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': 'Failed to update user information'}, status=400)

        elif label == 'changePassword':
            current_password = json_data.get('currentPassword')
            new_password = json_data.get('newPassword')

            # 检查当前密码是否正确
            if current_password != conn.pwd:
                return JsonResponse({'error': '当前密码不正确，请重试'}, status=400)

            # 如果一切正常，更新密码并返回成功消息
            conn.pwd = new_password
            saconn = sa_connection()

            try:
                conn.close_connection()
                execute(saconn, 'delete_user', (conn.userid,))
                execute(saconn, 'create_user', (conn.userid, new_password, 'U'))
                conn.relink()
                saconn.close()
                return JsonResponse({'message': '密码修改成功！'}, status=200)
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': '后台报错'}, status=400)
        elif label == 'photo':
            photo=json_data.get('image_data')
            photo=base64.b64decode(photo)

            try:
                sql='update auditor set photo=%s where auditorid=%s'
                update(conn.connection,sql,(photo,conn.userid))
                return JsonResponse({'message': '密码修改成功！'}, status=200)
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': '后台报错'}, status=400)




def uh(request):
    if request.method == 'GET':
        sql = 'select HRphoto as photo,HRUSER.HRid as userid,phone as telephone,HRname as name,enterprisename,hruser.enterpriseid as enterpriseid from HRUser,enterprise where hrid=%s and (HRUser.enterpriseid=enterprise.enterpriseid or hruser.enterpriseid is null)'
        result = select_with_para(conn.connection, sql, (str(conn.userid)))
        if result[0]['photo']:
            binary_image_data = result[0]['photo']
            # 将二进制图片数据转换为base64编码字符串
            base64_image_data = base64.b64encode(binary_image_data).decode('utf-8')
        else:
            base64_image_data = ''
        # 传递base64编码的图片数据给模板
        return render(request, 'role/uh.html', {'image_data': base64_image_data,
                                                'userid': result[0]['userid'],
                                                'telephone': result[0]['telephone'],
                                                'name': result[0]['name'],
                                                'enterprisename': result[0]['enterprisename'],
                                                'enterpriseid': result[0]['enterpriseid']} )
    if request.method == 'POST':
        body_data = request.body

        # 将字节字符串解码为字符串
        body_text = body_data.decode('utf-8')

        # 将字符串解析为JSON对象
        json_data = json.loads(body_text)
        label = json_data.get('label')
        if label == 'data':

            userid = json_data.get('userId')
            telephone = json_data.get('phone')
            name = json_data.get('name')
            enterprise = json_data.get('enterprise')
            enterpriseid = json_data.get('enterpriseid')

            sql = 'update HRuser set phone=%s, hrname=%s, enterpriseid=%s where hrid=%s'
            try:
                insert(conn.connection, sql, (
                telephone,
                name.encode('cp936'),enterpriseid, userid))
                return JsonResponse({'message': 'User information updated successfully'})
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': 'Failed to update user information'}, status=400)

        elif label == 'changePassword':
            current_password = json_data.get('currentPassword')
            new_password = json_data.get('newPassword')

            # 检查当前密码是否正确
            if current_password != conn.pwd:
                return JsonResponse({'error': '当前密码不正确，请重试'}, status=400)

            # 如果一切正常，更新密码并返回成功消息
            conn.pwd = new_password
            saconn = sa_connection()

            try:
                conn.close_connection()
                execute(saconn, 'delete_user', (conn.userid,))
                execute(saconn, 'create_user', (conn.userid, new_password, 'U'))
                conn.relink()
                saconn.close()
                return JsonResponse({'message': '密码修改成功！'}, status=200)
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': '后台报错'}, status=400)

        elif label == 'photo':
            photo=json_data.get('image_data')
            photo=base64.b64decode(photo)

            try:
                sql='update hruser set hrphoto=%s where hrid=%s'
                update(conn.connection,sql,(photo,conn.userid))
                return JsonResponse({'message': '密码修改成功！'}, status=200)
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': '后台报错'}, status=400)



def job_list(request):
    if request.method == 'GET':
        sql='''select jobid,
jobname,
tag,
pass_audit.cityid,
cityname,
districtid,
districtname,
experience_need,
edu_need,
job_discription,
job_discription,
enterprise.enterpriseid as enterpriseid,
enterprise.enterprisename as enterprisename,
createtime,
auditorid,
auditorname,
audittime,
max_salary,
min_salary,
job_hrid,
job_hrname,
 [enterpriselogo] from pass_audit,enterprise where pass_audit.enterpriseid=enterprise.enterpriseid'''
        jobs=select(conn.connection,sql)

        for idx,photo in enumerate(jobs[:]):
            jobs[idx]['enterpriselogo']=shift_image(photo['enterpriselogo'])

        sql='select provincename,cityname,districtname from district,city,province where district.cityid=city.cityid and province.provinceid=city.provinceid'
        district=select(conn.connection,sql)
        return render(request,'joblist.html',{'jobs':jobs,'district':district})
    elif request.method == 'POST':
        body_data = request.body

        # 将字节字符串解码为字符串
        body_text = body_data.decode('utf-8')

        # 将字符串解析为JSON对象
        json_data = json.loads(body_text)
        label = json_data.get('label')
        if label == 'apply':

            jobid=json_data.get('jobid')
            sql='insert into RJ([jobid],[userid]) values(%s,%s)'
            try:
                insert(conn.connection, sql, (jobid,conn.userid))
                return JsonResponse({'message': 'User information updated successfully'})
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': 'Failed to update user information'}, status=400)

def choose(request):
    if request.method == 'GET':
        sql='''select RJ.[userid],[jobname]
      ,[tag],
      [pass],
      Rj.jobid
      ,[cityid]
      ,[cityname]
      ,[districtid]
      ,[districtname]
      ,[experience_need]
      ,[edu_need]
      ,[job_discription]
      ,[enterpriseid]
      ,[enterprisename]
      ,[createtime]
      ,[auditorid]
      ,[auditorname]
      ,[audittime]
      ,[max_salary]
      ,[min_salary]
      ,[job_hrid]
      ,[job_hrname] from pass_audit,RJ where job_hrid=%s and Rj.jobid=pass_audit.jobid'''
        jobs=select_with_para(conn.connection,sql,(conn.userid))
        sql='select provincename,cityname,districtname from district,city,province where district.cityid=city.cityid and province.provinceid=city.provinceid'
        district=select(conn.connection,sql)
        return render(request,'choose.html',{'jobs':jobs,'district':district})
    elif request.method == 'POST':
        body_data = request.body

        # 将字节字符串解码为字符串
        body_text = body_data.decode('utf-8')

        # 将字符串解析为JSON对象
        json_data = json.loads(body_text)
        label = json_data.get('label')
        if label == 'choose':

            jobid=json_data.get('jobid')
            userid=json_data.get('userid')
            status=json_data.get('status')
            print(jobid,userid,status)
            try:
                sa=sa_connection()
                if status == 'pass':
                    execute(sa,'[dbo].[set_pass]',(jobid,userid))
                else:
                    execute(sa, '[dbo].[set_fail]', (jobid, userid))
                sa.close()
                return JsonResponse({'message': 'User information updated successfully'})
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': 'Failed to update user information'}, status=400)

def interview(request):
    if request.method == 'GET':
        sql = '''select RJ.[userid],[jobname]
      ,[tag],
      [interviewResult],
      Rj.jobid
      ,[cityid]
      ,[cityname]
      ,[districtid]
      ,[districtname]
      ,[experience_need]
      ,[edu_need]
      ,[job_discription]
      ,[enterpriseid]
      ,[enterprisename]
      ,[createtime]
      ,[auditorid]
      ,[auditorname]
      ,[audittime]
      ,[max_salary]
      ,[min_salary]
      ,[job_hrid]
      ,[job_hrname] from pass_audit,RJ where job_hrid=%s and Rj.jobid=pass_audit.jobid and pass=%s'''
        jobs = select_with_para(conn.connection, sql, (conn.userid,'通过'.encode('cp936')))
        sql = 'select provincename,cityname,districtname from district,city,province where district.cityid=city.cityid and province.provinceid=city.provinceid'
        district = select(conn.connection, sql)
        return render(request, 'interview.html', {'jobs': jobs, 'district': district})
    elif request.method == 'POST':
        body_data = request.body

        # 将字节字符串解码为字符串
        body_text = body_data.decode('utf-8')

        # 将字符串解析为JSON对象
        json_data = json.loads(body_text)
        label = json_data.get('label')
        if label == 'choose':

            jobid = json_data.get('jobid')
            userid = json_data.get('userid')
            status = json_data.get('status')
            print(jobid, userid, status)
            try:
                sa = sa_connection()
                if status == 'pass':
                    execute(sa, '[dbo].[set_interview_pass]', (jobid, userid))
                else:
                    execute(sa, '[dbo].[set_interview_fail]', (jobid, userid))
                sa.close()
                return JsonResponse({'message': 'User information updated successfully'})
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': 'Failed to update user information'}, status=400)


def audit(request):
    if request.method == 'GET':
        sql = '''  select * from wait_for_audit'''
        jobs = select(conn.connection,sql)
        return render(request, 'audit.html', {'jobs': jobs})
    elif request.method == 'POST':
        body_data = request.body

        # 将字节字符串解码为字符串
        body_text = body_data.decode('utf-8')

        # 将字符串解析为JSON对象
        json_data = json.loads(body_text)
        label = json_data.get('label')
        if label == 'choose':

            jobid = json_data.get('jobid')
            status = json_data.get('status')
            reason = json_data.get('reason')
            print(jobid, status)
            try:
                sa = sa_connection()
                if status == 'pass':
                    execute(sa, '[dbo].[set_audit_pass]', (jobid,))
                else:
                    execute(sa, '[dbo].[set_audit_fail]', (jobid,reason.encode('cp936')))
                sql='update job set [audtittime]=getdate(),[auditorid]=%s'
                update(sa,sql,(conn.userid))
                sa.close()
                return JsonResponse({'message': 'User information updated successfully'})
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': 'Failed to update user information'}, status=400)


def createjob(request):
    if request.method == 'GET':
        sql='''  select jobid,jobname,tag,job.cityid as cityid,city.cityname as cityname,job.districtid as districtid,districtname,experience_need,edu_need,job_discription,job.enterpriseid as enterpriseid,enterprisename,createtime,
job.auditorid,auditorname,[audtittime],max_salary,min_salary,job.hrid as job_hrid,hrname as job_hrname,auditresult
from job left join enterprise on(job.enterpriseid=enterprise.enterpriseid) left join city on(job.cityid=city.cityid)
left join district on (district.districtid=job.districtid) left join auditor on (job.auditorid=auditor.auditorid)
left join HRUser on (job.HRid=HRUser.HRid) where enterprise.enterpriseid=%s'''
        jobs=select_with_para(conn.connection,sql,conn.userid)
        sql='select provincename,cityname,districtname from district,city,province where district.cityid=city.cityid and province.provinceid=city.provinceid'
        district=select(conn.connection,sql)
        sql='select jobnum from enterprise where enterpriseid=%s'
        jobnum=select_with_para(conn.connection,sql,(conn.userid))[0]['jobnum']
        sql = 'select hrid,hrname from hruser where enterpriseid=%s'
        hrs = select_with_para(conn.connection, sql, (str(conn.userid)))
        sql="select cityname from city"
        city = select(conn.connection, sql)
        return render(request,'createjob.html',{'jobs':jobs,'district':district,'jobnum':jobnum,'hrs':hrs,'cities':city})
    elif request.method == 'POST':
        body_data = request.body

        # 将字节字符串解码为字符串
        body_text = body_data.decode('utf-8')

        # 将字符串解析为JSON对象
        json_data = json.loads(body_text)
        label = json_data.get('label')

        if label == 'create':
            jobid="{:05}".format((random.randint(1,99999)))+"{:04}".format(random.randint(0,9999))
            jobName=json_data.get('jobName')
            maxSalary=json_data.get('maxSalary')
            minSalary=json_data.get('minSalary')
            tag=json_data.get('tag')
            city=json_data.get('city')
            experience=json_data.get('experience')
            education=json_data.get('education')
            description=json_data.get('description')
            district=json_data.get('district')
            hrid=json_data.get('hrid')
            sql='select cityid from city where cityname=%s'
            print(city,district)
            city=select_with_para(conn.connection,sql,(city.rstrip().encode('cp936')))[0]['cityid']
            sql='select districtid from district where districtname=%s'
            district=select_with_para(conn.connection,sql,(district.rstrip().encode('cp936')))[0]['districtid']
            sql='''insert into job(jobid,jobname,tag,cityid,[experience_need],[edu_need],[job_discription],[enterpriseid],[HRid],[max_salary],[min_salary],districtid) 
            values(%s,%s,%s,%s,%d,%s,%s,%s,%s,%d,%d,%s)'''
            try:
                print(jobid,jobName,tag,city,experience,education,description,conn.userid,hrid,maxSalary,minSalary,district)
                insert(sa_connection(), sql, (jobid,jobName.encode('cp936'),tag.encode('cp936'),city,experience,education.encode('cp936'),description.encode('cp936'),conn.userid,hrid,maxSalary,minSalary,district))
                return JsonResponse({'message': 'User information updated successfully'})
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': 'Failed to update user information'}, status=400)

        if label == 'update':
            jobid=json_data.get('jobid')
            jobName=json_data.get('jobName')
            maxSalary=json_data.get('maxSalary')
            minSalary=json_data.get('minSalary')
            tag=json_data.get('tag')
            city=json_data.get('city')
            experience=json_data.get('experience')
            education=json_data.get('education')
            description=json_data.get('description')
            district=json_data.get('district')
            hrid=json_data.get('hrid')

            sql='select cityid from city where cityname=%s'

            city=select_with_para(conn.connection,sql,(city.rstrip().encode('cp936')))[0]['cityid']
            sql='select districtid from district where districtname=%s'
            district=select_with_para(conn.connection,sql,(district.rstrip().encode('cp936')))[0]['districtid']
            sql='''update job set jobname=%s,tag=%s,cityid=%s,experience_need=%d,edu_need=%s,job_discription=%s,HRid=%s,max_salary=%d,min_salary=%d,districtid=%s where jobid=%s'''
            # sql = '''update job set jobname=%s,tag=%s,cityid=%s,experience_need=%d,edu_need=%s,job_discription=%s,HRid=%s,max_salary=%d,min_salary=%d, where jobid=%s'''

            try:
                update(sa_connection(), sql, (jobName.encode('cp936'),tag.encode('cp936'),city,experience,education.encode('cp936'),description.encode('cp936'),hrid,maxSalary,minSalary,district,jobid))
                # update(sa_connection(), sql, (
                # jobName.encode('cp936'), tag.encode('cp936'), city, experience, education.encode('cp936'),
                # description.encode('cp936'), conn.userid, hrid, maxSalary, minSalary, district, jobid))

                return JsonResponse({'message': 'User information updated successfully'})
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': 'Failed to update user information'}, status=400)
        if label == 'delete':
            jobid=json_data.get('jobid')
            sql='delete from job where jobid=%s'

            try:
                sa=sa_connection()
                delete(sa, sql, (jobid))
                sa.close()
                return JsonResponse({'message': 'User information updated successfully'})
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': 'Failed to update user information'}, status=400)


def register(request):
    if request.method == 'GET':
        return render(request,'register.html')
    elif request.method == 'POST':
        body_data = request.body

        # 将字节字符串解码为字符串
        body_text = body_data.decode('utf-8')

        # 将字符串解析为JSON对象
        json_data = json.loads(body_text)
        label = json_data.get('label')
        if label == 'register':
            identify=json_data.get('identity')
            username=json_data.get('username')
            password=json_data.get('password')
            type=json_data.get('type')
            print(identify,username,password)
            if identify=='user':
                id=str(random.randint(1000,9999))+"{:06}".format(random.randint(1,100000))
                sql='insert into ruser(userid,name,code) values(%s,%s,%s)'

                iden='U'
            if identify=='company':
                id='{:07d}'.format(random.randint(100,999))
                iden='E'
                sql='insert into enterprise(enterpriseid,enterprisename,code,type1) values(%s,%s,%s,%s)'
                try:
                    sa = sa_connection()
                    execute(sa, 'create_user', (id, password, iden))
                    update(sa, sql, (id, username.encode('cp936'), password,type.encode('cp936')))
                    sa.close()
                    return JsonResponse({'message': 'User information updated successfully', 'userid': id})
                except Exception as e:
                    print("Error:", e)
                    return JsonResponse({'error': 'Failed to update user information'}, status=400)
            if identify=='hr':
                id=str(random.randint(1000,9999))+"{:04}".format(random.randint(1,9999))
                iden='H'
                sql='insert into hruser(hrid,hrname,code) values(%s,%s,%s)'


            try:
                sa=sa_connection()
                execute(sa,'create_user',(id,password,iden))
                update(sa,sql,(id,username.encode('cp936'),password))
                sa.close()
                return JsonResponse({'message': 'User information updated successfully','userid':id})
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': 'Failed to update user information'}, status=400)

def job_detail(request, job_id):
    job_id="{:09}".format(job_id)
    # 根据传递的 job_id 参数从数据库中获取相应的岗位信息
    sql='select * from job where jobid=%s'
    job=select_with_para(conn.connection,sql,(job_id))
    # 将岗位信息传递给模板
    return render(request, 'jobInfo.html', {'job': job[0]})


def interviewResult(request):
    if request.method == 'GET':
        sql = '''select RJ.[userid],[jobname]
      ,[tag],
      [interviewResult],
      Rj.jobid
      ,[cityid]
      ,[cityname]
      ,[districtid]
      ,[districtname]
      ,[experience_need]
      ,[edu_need]
      ,[job_discription]
      ,[enterpriseid]
      ,[enterprisename]
      ,[createtime]
      ,[auditorid]
      ,[auditorname]
      ,[audittime]
      ,[max_salary]
      ,[min_salary]
      ,[job_hrid]
      ,[job_hrname] from pass_audit,RJ where enterpriseid=%s and Rj.jobid=pass_audit.jobid and interviewResult=%s'''
        jobs = select_with_para(conn.connection, sql, (conn.userid,'通过'.encode('cp936')))
        sql = 'select provincename,cityname,districtname from district,city,province where district.cityid=city.cityid and province.provinceid=city.provinceid'
        district = select(conn.connection, sql)
        return render(request, 'interviewResult.html', {'jobs': jobs, 'district': district})


def ur_show(request,userid):
    job_id = "{:010}".format(userid)
    # 根据传递的 job_id 参数从数据库中获取相应的岗位信息
    resumes = []
    if request.method == 'GET':
        sql = 'select photo,userid,telephone,Raddress,highestEdu,experience,age,name,sex from Ruser where userid=%s'
        result = select_with_para(conn.connection, sql, (str(userid)))
        if result[0]['photo']:
            binary_image_data = result[0]['photo']
            # 将二进制图片数据转换为base64编码字符串
            base64_image_data = base64.b64encode(binary_image_data).decode('utf-8')
        else:
            base64_image_data = ''
        sql = 'select * from resume where userid=%s'

        resume = select_with_para(conn.connection, sql, (str(userid)))
        resumes = [i['resumeid'] for i in resume]
        sql = 'select schoolname,schoolLogo,schooltype,degree,major,finishdate from [dbo].[college_education_experience],school where userid=%s and [college_education_experience].schoolid=school.schoolid'
        education_experience = select_with_para(conn.connection, sql, (str(userid)))
        if len(education_experience) != 0:
            for ee in education_experience:
                ee['schoolLogo'] = shift_image(ee['schoolLogo'])
                ee['finishdate'] = str(ee['finishdate'])

        sql = 'select * from school'
        school = select(conn.connection, sql)
        for ss in school:
            ss['schoolLogo'] = shift_image(ss['schoolLogo'])
            ss['schoolname'] = ss['schoolname'].rstrip()
        # 传递base64编码的图片数据给模板
        return render(request, 'roleShow/ur.html', {'image_data': base64_image_data,
                                                'userid': result[0]['userid'],
                                                'telephone': result[0]['telephone'],
                                                'Raddress': result[0]['Raddress'],
                                                'highestEdu': result[0]['highestEdu'],
                                                'experience': result[0]['experience'],
                                                'age': result[0]['age'],
                                                'name': result[0]['name'],
                                                'sex': result[0]['sex'],
                                                'resume': [re['advantages'].rstrip() for re in resume],
                                                'lengths': len([re['advantages'] for re in resume]),
                                                'education_experience': education_experience,
                                                'lengths_of_education_experience': len(education_experience),
                                                'school': school},

                      )

def ue_show(request,userid):
    userid = "{:07}".format(userid)
    if request.method == 'GET':
        print(userid)
        sql = 'select enterpriselogo as photo,enterpriseid as userid,enterpriseaddress as Raddress,enterprisename as name,type1,type2,introduction,city.cityname from enterprise,city where enterpriseid=%s and enterprise.cityid=city.cityid'
        result = select_with_para(conn.connection, sql, (str(userid)))
        if result[0]['photo']:
            binary_image_data = result[0]['photo']
            # 将二进制图片数据转换为base64编码字符串
            base64_image_data = base64.b64encode(binary_image_data).decode('utf-8')
        else:
            base64_image_data = ''
        sql = 'select * from resume where userid=%s'

        resume = select_with_para(conn.connection, sql, (str(userid)))
        resumes = [i['resumeid'] for i in resume]
        # 传递base64编码的图片数据给模板
        return render(request, 'roleShow/ue.html', {'image_data': base64_image_data,
                                                'userid': result[0]['userid'],
                                                'Raddress': result[0]['Raddress'],
                                                'name': result[0]['name'],
                                                'introduction': result[0]['introduction'].rstrip(),
                                                'city': result[0]['cityname'],
                                                'type1': result[0]['type1'],
                                                'type2': result[0]['type2'],
                                                }, )



def uh_show(request,userid):
    userid = "{:08}".format(userid)
    if request.method == 'GET':
        sql = 'select HRphoto as photo,HRUSER.HRid as userid,phone as telephone,HRname as name,enterprisename,hruser.enterpriseid as enterpriseid from HRUser,enterprise where hrid=%s and HRUser.enterpriseid=enterprise.enterpriseid'
        result = select_with_para(conn.connection, sql, (str(userid)))
        if result[0]['photo']:
            binary_image_data = result[0]['photo']
            # 将二进制图片数据转换为base64编码字符串
            base64_image_data = base64.b64encode(binary_image_data).decode('utf-8')
        else:
            base64_image_data = ''
        # 传递base64编码的图片数据给模板
        return render(request, 'roleShow/uh.html', {'image_data': base64_image_data,
                                                'userid': result[0]['userid'],
                                                'telephone': result[0]['telephone'],
                                                'name': result[0]['name'],
                                                'enterprisename': result[0]['enterprisename'],
                                                'enterpriseid': result[0]['enterpriseid']})



def result(request):
    if request.method == 'GET':
        sql='''select 
        [pass],[interviewResult],[choosetime],
        RJ.[jobid]
      ,[jobname]
      ,[tag]
      ,[cityid]
      ,[cityname]
      ,[districtid]
      ,[districtname]
      ,[experience_need]
      ,[edu_need]
      ,[job_discription]
      ,[enterpriseid]
      ,[enterprisename]
      ,[createtime]
      ,[auditorid]
      ,[auditorname]
      ,[audittime]
      ,[max_salary]
      ,[min_salary]
      ,[job_hrid]
      ,[job_hrname] from pass_audit,RJ where RJ.jobid=pass_audit.jobid and RJ.userid=%s'''
        jobs=select_with_para(conn.connection,sql,conn.userid)
        sql='select provincename,cityname,districtname from district,city,province where district.cityid=city.cityid and province.provinceid=city.provinceid'
        district=select(conn.connection,sql)
        return render(request,'result.html',{'jobs':jobs,'district':district})

def history(request):
    if request.method == 'GET':
        sql = 'select * from pass_audit'
        jobs = select_with_para(conn.connection, sql,(conn.userid))
        sql = 'select provincename,cityname,districtname from district,city,province where district.cityid=city.cityid and province.provinceid=city.provinceid'
        district = select(conn.connection, sql)
        return render(request, 'history.html', {'jobs': jobs, 'district': district})
    elif request.method == 'POST':
        body_data = request.body

        # 将字节字符串解码为字符串
        body_text = body_data.decode('utf-8')

        # 将字符串解析为JSON对象
        json_data = json.loads(body_text)
        label = json_data.get('label')
        if label == 'choose':

            jobid = json_data.get('jobid')
            status = json_data.get('status')
            reason = json_data.get('reason')
            print(jobid, status)
            try:
                sa = sa_connection()
                if status == 'pass':
                    execute(sa, '[dbo].[set_audit_pass]', (jobid,))
                else:
                    execute(sa, '[dbo].[set_audit_fail]', (jobid,reason.encode('cp936')))
                sql='update job set [audtittime]=getdate(),[auditorid]=%s'
                update(sa,sql,(conn.userid))
                sa.close()
                return JsonResponse({'message': 'User information updated successfully'})
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'error': 'Failed to update user information'}, status=400)


# if __name__=='__main__':
#     conn = open_connection(userid, pwd)
#     sql='select * from pass_audit'
#     district = select(conn, sql)
#     print(district)