#from tabulate import tabulate

class Student:
    def __init__(self,nr,nume,  medie,):
        self.nume=str(nume)
        self.medie=medie
    def Binary_Search():
        media_cautata=int(input("media cautata:\n"))
        low=0
        high=10
        mid=0
        ok=0
        while(low<=high):
            mid=int((high+low)/2)
            if(student[mid].medie<media_cautata):
                low=mid+1
                ok=1
            elif(student[mid].medie>media_cautata):
                high=mid-1
                ok=1
            else:
                return(str(student[mid].nume))
          
        print("Nici un student nu are media "+ str(media_cautata))
    def Sequential_Search():
        ok=0
        nume_cautat=str(input("Numele studentului cautat:\n"))
        for i in range(10):
            if(str(student[i].nume)==nume_cautat):
                print("Studentul " + nume_cautat + " se afla pe pozitia " + str(i) + " si are media " + str(student[i].medie))
                #return(student[i].medie)
                ok=int(1)
        if(int(ok)==0):
            print("Studentul "+ str(nume_cautat) + " nu exista in registrul studentilor")
student=[]

student.append(Student(0, "Dima", 1))
student.append(Student(1, "Stefan", 5))
student.append(Student(2, "Andrei", 5))
student.append(Student(3, "Grigore", 6))
student.append(Student(4, "Catalin", 7))
student.append(Student(5, "Sorin", 8))
student.append(Student(6, "Claudiu",8 ))
student.append(Student(7, "Nicolae", 9))
student.append(Student(8, "Sebastian",9 ))
student.append(Student(9, "Ana",10 ))
class Instantiator:
    def main():
        z=int(input("Pentru cautarea dupa medie apasati tasa 1, iar pentru cautarea dupa student apasati tasta 2 \n"))
        if(z==1):
            print("studentul "+ Student.Binary_Search() + " are media cautata ")
        elif(z==2):
            Student.Sequential_Search()
        else:
            print("nu ati ales nici o variabila corecta, programul se va opri") 
Instantiator.main()