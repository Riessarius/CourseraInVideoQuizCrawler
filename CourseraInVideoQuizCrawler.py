# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 13:58:17 2019

@author: tigre
"""

import requests
import json
import time

programStartTime = time.time()

COURSE_NAME = r"" # Put your course name here, which you can get from the url of the homepage. E.g. machine-learning
COURSE_ID = r"" # Put your course ID here, which you can get from the related network traffic. E.g. Gtv4Xb1-EeS-ViIACwYKVQ
USER_ID = r"" # Put your user ID here, which you can get from the related network traffic.
USER_AGENT = r"" # Put an user agent here. E.g. Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36
CONTENT_TYPE = r"application/json; charset=UTF-8"
COOKIE = r"""""" # Put your cookie here, which you can get from the related network traffic.
COURSERA_API_URL = "https://www.coursera.org/api"
RESULT_FILE_LOC = "" # Indicate a file to store the result. E.g. result.txt

universalHeaders = {
        "user-agent" : USER_AGENT,
        "content-type" : CONTENT_TYPE,
        "cookie" : COOKIE
        }

courseItemUrl = COURSERA_API_URL + "/onDemandCourseMaterials.v2"
courseItemParams = {
        "q" : r"slug",
        "slug" : COURSE_NAME,
        "includes" : r"modules,lessons,passableItemGroups,passableItemGroupChoices,passableLessonElements,items,tracks,gradePolicy,gradingParameters",
        "fields" : r"""moduleIds,onDemandCourseMaterialModules.v1(name,slug,description,timeCommitment,lessonIds,optional,learningObjectives),onDemandCourseMaterialLessons.v1(name,slug,timeCommitment,elementIds,optional,trackId),onDemandCourseMaterialPassableItemGroups.v1(requiredPassedCount,passableItemGroupChoiceIds,trackId),onDemandCourseMaterialPassableItemGroupChoices.v1(name,description,itemIds),onDemandCourseMaterialPassableLessonElements.v1(gradingWeight,isRequiredForPassing),onDemandCourseMaterialItems.v2(name,slug,timeCommitment,contentSummary,isLocked,lockableByItem,itemLockedReasonCode,trackId,lockedStatus,itemLockSummary),onDemandCourseMaterialTracks.v1(passablesCount),onDemandGradingParameters.v1(gradedAssignmentGroups)""",
        "showLockedItems" : "true"
        }
courseItemResponse = requests.get(courseItemUrl, courseItemParams)

courseItemList = []

print("Gathering the vidoes...")
for citem in courseItemResponse.json()["linked"]["onDemandCourseMaterialItems.v2"] :
    if citem["contentSummary"]["typeName"] == "lecture" :
        courseItemList.append(citem["id"])

videoQuestionList = []

for courseItem in courseItemList :
    print("Analyzing video %s..." % courseItem)
    videoQuestion = {}
    
    videoIdUrl = COURSERA_API_URL + "/onDemandLectureVideos.v1/" + COURSE_ID + "~" + courseItem
    videoIdParams = {
            "includes" : "video",
            "fields" : r"""onDemandVideos.v1(sources,subtitles,subtitlesVtt,subtitlesTxt)"""
            }
    videoIdResponse = requests.get(videoIdUrl, params = videoIdParams)
    videoQuestion["videoId"] = videoIdResponse.json()["linked"]["onDemandVideos.v1"][0]["id"]
    
    videoQuestion["questions"] = []
    questionSessionUrl = COURSERA_API_URL + "/opencourse.v1/user/" + str(USER_ID) + "/course/" + COURSE_NAME + "/item/" + courseItem + "/lecture/inVideoQuiz/session"
    questionSessionPayload = {
            "contentRequestBody": {}
            }
    questionSessionResponse = requests.post(questionSessionUrl, headers = universalHeaders, json = questionSessionPayload)
    if questionSessionResponse.status_code == 200 :
        questionSession = questionSessionResponse.json()["contentResponseBody"]["session"]["id"]
        getQuestionUrl = questionSessionUrl + "/" + questionSession + "/action/getQuestions"
        getQuestionParams = {
                "autoEnroll" : False
                }
        getQuestionPayload = {
                "contentRequestBody" : {
                            "argument" : {}
                        }
                }
        getQuestionResponse = requests.post(getQuestionUrl, params = getQuestionParams, headers = universalHeaders, json = getQuestionPayload)
        
        for qitem in getQuestionResponse.json()["contentResponseBody"]["return"]["questions"] :
            question = {}
            question["id"] = qitem["id"]
            question["type"] = qitem["question"]["type"]
            question["definition"] = qitem["variant"]["prompt"]["definition"]["value"][12 : -13]
            question["options"] = []
            
            for oitem in qitem["variant"]["options"] :
                option = {}
                option["id"] = oitem["id"]
                option["content"] = oitem["display"]["definition"]["value"][12 : -13]
                question["options"].append(option)
            
            question["answer"] = []
            question["explanation"] = ""
            if question["type"] == "mcq" :
                submitResponseUrl = questionSessionUrl + "/" + questionSession + "/action/submitResponse"
                submitResponseParams = {
                "autoEnroll" : False
                }
                submitResponsePayload = {
                        "contentRequestBody" : {
                                "argument" : {
                                        "timestamp" : None,
                                        "questionInstance" : question["id"],
                                        "response" : {}
                                        }
                                }
                        }
                for oitem in question["options"]:
                    submitResponsePayload["contentRequestBody"]["argument"]["response"]["chosen"] = oitem["id"]
                    submitResponseResponse = requests.post(submitResponseUrl, params = submitResponseParams, headers = universalHeaders, json = submitResponsePayload)
                    if submitResponseResponse.json()["contentResponseBody"]["return"]["feedback"]["definition"]["isCorrect"] == True :
                        question["answer"].append(oitem["id"])
                        question["explanation"] = submitResponseResponse.json()["contentResponseBody"]["return"]["feedback"]["definition"]["display"]["definition"]["value"][12 : -13]
                        break
            elif question["type"] == "checkbox" :
                submitResponseUrl = questionSessionUrl + "/" + questionSession + "/action/submitResponse"
                submitResponseParams = {
                        "autoEnroll" : False
                        }
                submitResponsePayload = {
                        "contentRequestBody" : {
                                "argument" : {
                                        "timestamp" : None,
                                        "questionInstance" : question["id"],
                                        "response" : {
                                                "chosen" : []
                                                }
                                        }
                                }
                        }
                submitResponseResponse = requests.post(submitResponseUrl, params = submitResponseParams, headers = universalHeaders, json = submitResponsePayload)
                for oitem in submitResponseResponse.json()["contentResponseBody"]["return"]["feedback"]["definition"]["options"]:
                    if oitem["isCorrect"] == False :
                        question["answer"].append(oitem["id"])
                
            
            question["videoCuePoint"] = qitem["video"]["cuePointMs"]
            
            videoQuestion["questions"].append(question)
    
    videoQuestionList.append(videoQuestion)

print("Writing results into files...")
resultFile = open(RESULT_FILE_LOC, "w")
resultFile.write(json.dumps(videoQuestionList, indent = 4))
resultFile.close()

programEndTime = time.time()

programElapsedTime = programEndTime - programStartTime
print("Done! Total elapsed time: %ds..." % programElapsedTime)
