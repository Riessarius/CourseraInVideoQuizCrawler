# Coursera In-Video-Quiz Crawler
A crawler to extract all in-video-quizzes in a course on Coursera.



## Prerequisites

* Python 3.8
* Python Library: Requests 2.22.0



## Usage

* Fill the parameters in `CourseraInVideoQuizCrawler.py`.
* Run the script and wait.
* Collect results in the file.



## Mechanism

The general idea of this script is to collect all video links, iterate and find all quizzes, and obtain their solutions by trials. The results will be organized in JSON format.

### Collect video links

The homepage of a course on Coursera is  `https://www.coursera.org/learn/<COURSE_NAME>/home/welcome`. However you cannot receive links to any of its video page by sending a GET request of this URL because they will be inserted into the HTML by scripts later. All video links respectively have a 5-letter short ID (e.g. zuAcT) for discrimination, which you can see in the URL of any video page. These short IDs, not real video IDs though, are obtained by sending a GET request to `<COURSERA_API_URL>/onDemandCourseMaterials.v2`, with many parameters followed by. The script collects short IDs from the response. The real ID of a video can be obtained by sending a GET request to `<COURSERA_API_URL>/onDemandLectureVideos.v1/<COURSE_ID>`, with proper parameters.

### Find all quizzes in a video

If a video short ID is specified, the quizzes in this video can be obtained from the response by sending a POST request to `<COURSERA_API_URL>/opencourse.v1/user/<USER_ID>/course/<COURSE_NAME>/item/<COURSE_SHORT_ID>/lecture/inVideoQuiz/session/<QUESTION_SESSION_ID>/action/getQuestions`. The `<QUESTION_SESSION_ID>` should be obtained first for each video by sending a POST request to `<COURSERA_API_URL>/opencourse.v1/user/<USER_ID>/course/<COURSE_NAME>/item/<COURSE_SHORT_ID>/lecture/inVideoQuiz/session`. The question structures are listed in  subdirectory `["contentResponseBody"]["return"]["questions"]` of the response body.

### Obtain answers and solutions

Answers and solutions are obtained by trials. Typically the script obtains answers to multiple choice questions and checkboxes, while answers to other types of questions are not obtained. The script will send a POST request to `<COURSERA_API_URL>/opencourse.v1/user/<USER_ID>/course/<COURSE_NAME>/item/<COURSE_SHORT_ID>/lecture/inVideoQuiz/session/<QUESTION_SESSTION_ID>/action/submitResponse` with payloads which contains some replies to the quiz.

### Structure of the results

The results are organized in the following JSON format:

```json
[
	{
        "videoId": "6Ypr1hQ-EeeFZBJX5mIoyg",
        "questions": [
            {
                "id": "yeEoMxykEeeKxgq5rEPplg",
                "type": "checkbox",
                "definition": "<text>\"A computer program is said to learn...",
                "options": [
                    {
                        "id": "0.3217165089626439",
                        "content": "<text>Classify emails as spam or..."
                    },
                    {
                        "id": "0.6127126640150993",
                        "content": "<text>Watching you label emails..."
                    },
                    {
                        "id": "0.7664927352929847",
                        "content": "<text>The number (or fraction) of emails..."
                    },
                    {
                        "id": "0.7069224238394478",
                        "content": "<text>None of the above, this is not..."
                    }
                ],
                "answer": [
                    "0.3217165089626439"
                ],
                "explanation": "",
                "videoCuePoint": 194881
            }
        ]
    },
]
```

An example of extracted data is in `Results_MachineLearning.txt`.



## Origin

The reason I wrote this script is that I've attended a Web application course in university, and one day the vice professor distributed some exclusive open experiments, and I just picked this one somehow. Till now I still believe I've been struck onto head by a lightning or what because that explains why I forgot the reason that I chose this topic. I'm quite not good at coding a crawler, or anything related to dealing with the web frontend, at least before several days ago. At first I was sunk into the ocean of the network traffic, and I select Selenium to build my first solution and I was about to submit that version (now I think this one was too foolish and it won't be uploaded here), but luckily I received some help from my friends after, thus here comes the second version, which was built on Requests.

