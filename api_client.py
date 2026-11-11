import requests

url = "https://noemedefacto-1.onrender.com/course"

response = requests.get(url, timeout=60)

if response.status_code == 200:
    data = response.json()

    print("COURSE INFORMATION")
    print("Course Code:", data.get("course_code"))
    print("Course Title:", data.get("course_title"))
    print("Instructor:", data.get("instructor"))
else:
    print("Request failed.")
    print("Status Code:", response.status_code)
    print(response.text)
