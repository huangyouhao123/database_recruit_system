class Ruser:
    def __init__(self,userid,code,telephone,photo,Raddress,highestEdu,experience,age,name,sex):
        self.userid, self.code, self.telephone, self.photo, self.Raddress, self.highestEdu, self.experience, self.age, self.name, self.sex=(
            userid,code,telephone,photo,Raddress,highestEdu,experience,age,name,sex)

class Auditor:
    def __init__(self,audotorid,auditorname,sex,age,photo,audit_num,audit_num_monthly,code):
        self.audotorid, self.auditorname, self.sex, self.age, self.photo, self.audit_num, self.audit_num_monthly, self.code=(
            audotorid,auditorname,sex,age,photo,audit_num,audit_num_monthly,code)

class HRuser:
    def __init__(self,HRid,HRname,HRphoto,code,phone,enterpriseid):
        self.HRid, self.HRname, self.HRphoto, self.code, self.phone, self.enterpriseid=(
            HRid,HRname,HRphoto,code,phone,enterpriseid)

class Enterprise:
    def __init__(self,enterpriseid,enterprisename,type1,type2,enterpriseaddress,jobnum,introduction,code,enterpriselogo,cityid):
        self.enterpriseid, self.enterprisename, self.type1, self.type2, self.enterpriseaddress, self.jobnum, self.introduction, self.code, self.enterpriselogo, self.cityid=(
            enterpriseid,enterprisename,type1,type2,enterpriseaddress,jobnum,introduction,code,enterpriselogo,cityid)

class User:
    def __init__(self,id,password):
        self.id=id
        self.password=password

