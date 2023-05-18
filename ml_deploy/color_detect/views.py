from django.shortcuts import render,redirect
from joblib import load
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import cv2,os
from collections import Counter
from .forms import UserForm
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User,auth
from django.contrib.auth.decorators import login_required

def login(request):  
    if request.method=='POST':
        college_mail = request.POST['college_mail']
        password = request.POST['password']
        username = User.objects.get(email=college_mail.lower()).username
        user = auth.authenticate(username=username, password=password)
        
        if user is not None:
            auth.login(request,user)
            return redirect('main')
        elif User.objects.filter(email=college_mail).exists():
            messages.info(request,'College mail already exists, Check your password')
            return redirect('login')
        
        else:
            messages.info(request, "You are not Registered to this website, Please do it ") 
            return redirect('signup')  
        
    return render(request,'login.html')
  

def signup(request):
    if request.method == 'POST':
        firstname=request.POST['first_name']
        college_mail=request.POST['college_mail']
        password=request.POST['password']
        conf_password=request.POST['conf_password']
        username= firstname
        
        if password_check(password):
            if password == conf_password:
                if User.objects.filter(email=college_mail).exists():
                    messages.info(request,'ID already exists')
                    return redirect('signup')
                else:
                    user = User.objects.create_user(username=username, first_name = firstname, email=college_mail, password=password)
                    user.save()
                    return redirect('login')
            else:
                messages.info(request,'Password not matching')
                return redirect('signup')
        else:
            messages.info(request,'''Please enter a password that is at least 6 characters long, 
                          contains at least one uppercase letter and one alphanumeric character.''')
            return redirect('signup')
    else:
        return render(request,'signup.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('main')
    
def password_check(passwd):
    SpecialSym =['!', '@', '#', '$', '%', '~','&']
    val = True
    if len(passwd) < 6:
        val = False  
    if len(passwd) > 20:
        val = False  
    if not any(char.isdigit() for char in passwd):
        val = False 
    if not any(char.isupper() for char in passwd):
        val = False  
    if not any(char.islower() for char in passwd):
        val = False   
    if not any(char in SpecialSym for char in passwd):
        val = False
    if val:
        return val
    
def main(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('result')
    else:
        form = UserForm()
    return render(request, 'main.html', {'form': form})

def result(request):
    return render(request, 'result.html')


def RGB2HEX(color):
    return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

def get_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

def get_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

def get_colors(image, number_of_colors, show_chart):
    modified_image = cv2.resize(image, (600, 400), interpolation=cv2.INTER_AREA)
    modified_image = modified_image.reshape(modified_image.shape[0] * modified_image.shape[1], 3)
    
    clf = KMeans(n_clusters=number_of_colors)
    labels = clf.fit_predict(modified_image)
    
    counts = Counter(labels)
    counts = dict(sorted(counts.items()))
    
    center_colors = clf.cluster_centers_
    ordered_colors = [center_colors[i] for i in counts.keys()]
    hex_colors = [RGB2HEX(ordered_colors[i]) for i in counts.keys()]
    rgb_colors = [ordered_colors[i] for i in counts.keys()]
    
    # if show_chart:
    #     plt.figure(figsize=(8, 6))
    #     plt.pie(counts.values(), labels=hex_colors, colors=hex_colors)
    #     plt.savefig('static/chart.png')  # Save the chart as an image
    
    return ordered_colors

def plot_detected(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (600, 400), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  
    threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1]
  
    contours = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
  
    i = 0
    font = cv2.FONT_HERSHEY_SIMPLEX
    for contour in contours:
        if i == 0:
            i = 1
            continue
        
        x, y, w, h = cv2.boundingRect(contour)
        if w > 20 and h > 20:
            crop = img[y:y+h, x:x+w]
            clr = get_colors(crop, 1, False)
            cv2.rectangle(img, (x, y), (x+w, y+h), clr[0], 2)
            cv2.putText(img, get_name(clr)[0], (x, y), font, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    
    cv2.imwrite('static/detected.png', img)

samples = [
    [0, 0, 0], [255, 255, 255], [255, 250, 250], [240, 255, 255], [255, 255, 240], [240, 255, 240], [248, 248, 255],
    [255, 250, 240], [0, 0, 255], [0, 0, 205], [0, 0, 139], [0, 0, 128], [0, 191, 255], [0, 128, 0], [0, 100, 0],
    [34, 139, 34], [124, 252, 0], [50, 205, 50], [255, 0, 0], [128, 0, 0], [139, 0, 0], [165, 42, 42], [220, 20, 60],
    [255, 69, 0], [255, 140, 0], [255, 165, 0], [255, 255, 0], [255, 215, 0], [75, 0, 130], [128, 0, 128],
    [148, 0, 211], [238, 130, 238], [147, 112, 219], [255, 20, 147], [255, 192, 203], [255, 182, 193],
    [139, 69, 19], [160, 82, 45], [78, 34, 34], [154, 205, 50], [85, 107, 47], [107, 142, 35], [124, 252, 0],
    [127, 255, 0], [173, 255, 47], [0, 100, 0], [0, 128, 0], [34, 139, 34], [0, 255, 0], [50, 205, 50],
    [240, 128, 128], [233, 150, 122], [250, 128, 114], [255, 160, 122], [255, 140, 0], [255, 165, 0],
    [255, 69, 0], [218, 165, 32],[0, 255, 255], [255, 0, 255], [128, 128, 128], [192, 192, 192], [128, 128, 0], [128, 0, 128],
    [0, 128, 128], [128, 0, 0], [0, 128, 0], [0, 0, 128], [255, 255, 128], [255, 128, 255], [128, 255, 255],[0, 0, 0], [255, 255, 255], [255, 250, 250], [240, 255, 255], [255, 255, 240], [240, 255, 240], [248, 248, 255],
    [255, 250, 240], [0, 0, 255], [0, 0, 205], [0, 0, 139], [0, 0, 128], [0, 191, 255], [0, 128, 0], [0, 100, 0],
    [34, 139, 34], [124, 252, 0], [50, 205, 50], [255, 0, 0], [128, 0, 0], [139, 0, 0], [165, 42, 42], [220, 20, 60],
    [255, 69, 0], [255, 140, 0], [255, 165, 0], [255, 255, 0], [255, 215, 0], [75, 0, 130], [128, 0, 128],
    [148, 0, 211], [238, 130, 238], [147, 112, 219], [255, 20, 147], [255, 192, 203], [255, 182, 193],
    [139, 69, 19], [160, 82, 45], [78, 34, 34], [154, 205, 50], [85, 107, 47], [107, 142, 35], [124, 252, 0],
    [127, 255, 0], [173, 255, 47], [0, 100, 0], [0, 128, 0], [34, 139, 34], [0, 255, 0], [50, 205, 50],
    [240, 128, 128], [233, 150, 122], [250, 128, 114], [255, 160, 122], [255, 140, 0], [255, 165, 0],
    [255, 69, 0], [218, 165, 32],[0, 255, 255], [255, 0, 255], [128, 128, 128], [192, 192, 192], [128, 128, 0], [128, 0, 128],
    [0, 128, 128], [128, 0, 0], [0, 128, 0], [0, 0, 128], [255, 255, 128], [255, 128, 255], [128, 255, 255],[255, 255, 0], [128, 128, 128], [211, 211, 211], [169, 169, 169], [128, 128, 0], [128, 0, 0], [0, 128, 128],
    [0, 0, 128], [0, 255, 0], [0, 255, 255], [255, 255, 224], [224, 102, 255], [175, 238, 238]
]

y = [
    "black", "White", "White", "White", "White", "White", "White", "White", "blue", "blue", "blue", "blue",
    "blue", "green", "green", "green", "green", "green", "red", "red", "red", "red", "red", "orange", "orange",
    "orange", "yellow", "yellow", "indigo", "Purple", "violet", "violet", "purple", "pink", "pink", "pink",
    "brown", "brown", "brown", "green", "green", "green", "green", "green", "green", "green", "green", "green",
    "green", "pink", "pink", "pink", "pink", "orange", "orange", "orange", "orange", "orange",'yellow', 'gray', 
    'gray', 'gray', 'olive', 'maroon', 'teal', 'navy', 'lime', 'aqua', 'light yellow', 'purple', 'aqua',"black", 
    "White", "White", "White", "White", "White", "White", "White", "blue", "blue", "blue", "blue",
    "blue", "green", "green", "green", "green", "green", "red", "red", "red", "red", "red", "orange", "orange",
    "orange", "yellow", "yellow", "indigo", "Purple", "violet", "violet", "purple", "pink", "pink", "pink",
    "brown", "brown", "brown", "green", "green", "green", "green", "green", "green", "green", "green", "green",
    "green", "pink", "pink", "pink", "pink", "orange", "orange", "orange", "orange", "orange",'yellow', 'gray', 
    'gray', 'gray', 'olive', 'maroon', 'teal', 'navy', 'lime', 'aqua', 'light yellow', 'purple', 'aqua',"yellow", "gray", "gray", 
    "gray", "olive", "maroon", "teal", "navy", "lime", "aqua", "yellow", "purple", "light aqua"
]

model = KNeighborsClassifier(n_neighbors=3)
model.fit(samples, y)

def get_name(code):
    return model.predict(code)

def process_image(request):
    if request.method == 'POST' and request.FILES['photo']:
        # Get the uploaded image file
        image_file = request.FILES['photo']
        
        # Save the uploaded image temporarily
        with open('temp_image.jpg', 'wb') as file:
            for chunk in image_file.chunks():
                file.write(chunk)
        
        # Perform the necessary image processing and prediction
        image = get_image('temp_image.jpg')
        colors = get_colors(image, number_of_colors=8, show_chart=False)
        prediction = get_name(colors)
        
        plot_detected('temp_image.jpg')

        detected_image_path = os.path.join(settings.MEDIA_URL, 'detected.png')
        chart_image_path = os.path.join(settings.MEDIA_URL, 'chart.png')

        return render(request, 'result.html', {'prediction': prediction,'detected_image_path': detected_image_path,'chart_image_path': chart_image_path})

    return render(request, 'main.html')