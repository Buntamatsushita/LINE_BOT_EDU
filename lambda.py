import os
import sys
import datetime
import boto3
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,FlexSendMessage,FollowEvent
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
import logging
import json


logger = logging.getLogger()
logger.setLevel(logging.ERROR)

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    logger.error('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    logger.error('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

user_list = {}

def lambda_handler(event, context):
    if "x-line-signature" in event["headers"]:
        signature = event["headers"]["x-line-signature"]
    elif "X-Line-Signature" in event["headers"]:
        signature = event["headers"]["X-Line-Signature"]
    body = event["body"]
    ok_json = {"isBase64Encoded": False,
               "statusCode": 200,
               "headers": {},
               "body": ""}
    error_json = {"isBase64Encoded": False,
                  "statusCode": 500,
                  "headers": {},
                  "body": "Error"}
    
    
    @handler.add(FollowEvent)
    def handle_follow(event):
        profile = line_bot_api.get_profile(event.source.user_id)
        name = profile.display_name
        line_bot_api.reply_message(event.reply_token,TextSendMessage("こんにちは、"+name+"さん。\n困ったら”ヘルプ”と言ってください。\n質問したい場合は”質問”と送ってください。"))
        user_list[name] = {"main_subject":"0","subject":"0","question":"0","answer":"0"}
        id = profile.user_id
        user_list[name]["user_id"] = id
    
    @handler.add(MessageEvent, message=TextMessage)
    def handle_message(event):
        
        select = {"現代文についての質問":"現代文","古文についての質問":"古文","漢文についての質問":"漢文","数学Ⅰについての質問":"数Ⅰ","数学Ⅱについての質問":"数Ⅱ",
            "数学Ⅲについての質問":"数Ⅲ","数学Aについての質問":"数A","数学Bについての質問":"数B","数学Cについての質問":"数C","情報についての質問":"情報","日本史Aについての質問":"日本史A",
            "日本史Bについての質問":"日本史B","世界史Aについての質問":"世界史A","世界史Bについての質問":"世界史B","地理についての質問":"地理","現代社会についての質問":"現代社会","政治経済についての質問":"政治経済",
            "倫理についての質問":"倫理","コミュニケーション英語Ⅰについての質問":"コミュニケーション英語Ⅰ","コミュニケーション英語Ⅱについての質問":"コミュニケーション英語Ⅱ","コミュニケーション英語Ⅲについての質問":"コミュニケーション英語Ⅲ",
            "英語表現Ⅰについての質問":"英語表現Ⅰ","英語表現Ⅱについての質問":"英語表現Ⅱ","化学についての質問":"化学","化学基礎についての質問":"化学基礎","生物についての質問":"生物","生物基礎についての質問":"生物基礎","物理についての質問":"物理",
            "物理基礎についての質問":"物理基礎"}

        profile = line_bot_api.get_profile(event.source.user_id)
        name = profile.display_name
        
        
            
        if event.message.text == "ヘルプ":
            line_bot_api.reply_message(event.reply_token,TextSendMessage("質問したい場合は”質問”と送ってください。\nまた、質問取り消しを行う場合は”質問をやめる”と送ってください。"))
    
        elif user_list[name]["main_subject"] == "0" and event.message.text == "質問":  #教科選択
            account = {"main_subject":"0","subject":"0","question":"0","answer":"0"}
            user_list[name] = account
            flex_message_json_string="""
                 {"type": "bubble",
                            "size": "mega",
                            "direction": "ltr",
                            "header": {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": "教科を選択",
                                    "align": "center",
                                    "contents": []
                                }
                                ]
                            },
                            "hero": {
                                "type": "image",
                                "url": "https://vos.line-scdn.net/bot-designer-template-images/bot-designer-icon.png",
                                "size": "xxs",
                                "aspectRatio": "1.51:1",
                                "aspectMode": "fit"
                            },
                            "body": {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                    "type": "message",
                                    "label": "国語",
                                    "text": "国語についての質問"
                                    }
                                },
                                {
                                    "type": "button",
                                    "action": {
                                    "type": "message",
                                    "label": "数学",
                                    "text": "数学についての質問"
                                    }
                                },
                                {
                                    "type": "button",
                                    "action": {
                                    "type": "message",
                                    "label": "理科",
                                    "text": "理科についての質問"
                                    }
                                }
                                ]
                            },
                            "footer": {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                    "type": "message",
                                    "label": "地歴公民",
                                    "text": "地歴公民についての質問"
                                    }
                                },
                                {
                                    "type": "button",
                                    "action": {
                                    "type": "message",
                                    "label": "英語",
                                    "text": "英語についての質問"
                                    }
                                }
                                ]
                            }
                            }
            """
            flex_message_json_dict = json.loads(flex_message_json_string)
            line_bot_api.reply_message(event.reply_token,
            FlexSendMessage(alt_text='alt_text',
                # contentsパラメタに, dict型の値を渡す
                contents=flex_message_json_dict
            ))
            
    
        elif event.message.text == "国語についての質問" and user_list[name]["main_subject"] == "0" :
            user_list[name]["main_subject"] = "国語"
            flex_message_json_string="""
                {
                "type": "bubble",
                "size": "mega",
                "direction": "ltr",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": "国語科",
                        "weight": "bold",
                        "size": "lg",
                        "align": "center",
                        "contents": []
                    }
                    ]
                },
                "hero": {
                    "type": "image",
                    "url": "https://vos.line-scdn.net/bot-designer-template-images/bot-designer-icon.png",
                    "size": "xxs",
                    "aspectRatio": "1.51:1",
                    "aspectMode": "fit"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "separator",
                        "margin": "none",
                        "color": "#FFFFFFFF"
                    }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "現代文",
                        "text": "現代文についての質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "古文",
                        "text": "古文についての質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "漢文",
                        "text": "漢文についての質問"
                        }
                    }
                    ]
                }
                }
            """
            flex_message_json_dict = json.loads(flex_message_json_string)
            line_bot_api.reply_message(event.reply_token,
            FlexSendMessage(alt_text='alt_text',
                # contentsパラメタに, dict型の値を渡す
                contents=flex_message_json_dict
            ))
    
    
        elif event.message.text == "数学についての質問" and user_list[name]["main_subject"] == "0":
            user_list[name]["main_subject"] = "数学"
            flex_message_json_string="""
                {
                "type": "bubble",
                "size": "mega",
                "direction": "ltr",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": "数学科",
                        "align": "center",
                        "contents": []
                    }
                    ]
                },
                "hero": {
                    "type": "image",
                    "url": "https://vos.line-scdn.net/bot-designer-template-images/bot-designer-icon.png",
                    "size": "xxs",
                    "aspectRatio": "1.51:1",
                    "aspectMode": "fit"
                },
                "body": {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "数Ⅰ",
                        "text": "数学Ⅰについての質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "数Ⅱ",
                        "text": "数学Ⅱについての質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "数Ⅲ",
                        "text": "数学Ⅲについての質問"
                        }
                    }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "数A",
                        "text": "数学Aについての質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "数B",
                        "text": "数学Bについての質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "数C",
                        "text": "数学Cについての質問"
                        }
                    }
                    ]
                }
                }
            """
            flex_message_json_dict = json.loads(flex_message_json_string)
            line_bot_api.reply_message(event.reply_token,
            FlexSendMessage(alt_text='alt_text',
                # contentsパラメタに, dict型の値を渡す
                contents=flex_message_json_dict
            ))
    
    
        elif event.message.text == "理科についての質問" and user_list[name]["main_subject"] == "0":
            user_list[name]["main_subject"] = "理科"
            flex_message_json_string="""
                {
                "type": "bubble",
                "size": "mega",
                "direction": "ltr",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": "理科",
                        "weight": "bold",
                        "size": "lg",
                        "align": "center",
                        "contents": []
                    }
                    ]
                },
                "hero": {
                    "type": "image",
                    "url": "https://vos.line-scdn.net/bot-designer-template-images/bot-designer-icon.png",
                    "size": "xxs",
                    "aspectRatio": "1.51:1",
                    "aspectMode": "fit"
                },
                "body": {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "化学",
                        "text": "化学についての質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "化基",
                        "text": "化学基礎についての質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "生物",
                        "text": "生物についての質問"
                        }
                    }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "生基",
                        "text": "生物基礎についての質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "物理",
                        "text": "物理についての質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "物基",
                        "text": "物理基礎についての質問"
                        }
                    }
                    ]
                }
                }
            """
            flex_message_json_dict = json.loads(flex_message_json_string)
            line_bot_api.reply_message(event.reply_token,
            FlexSendMessage(alt_text='alt_text',contents=flex_message_json_dict))
    
    
        elif event.message.text == "地歴公民についての質問" and user_list[name]["main_subject"] == "0":
            user_list[name]["main_subject"] = "地歴公民"
            flex_message_json_string="""
                {
                "type": "bubble",
                "size": "giga",
                "direction": "ltr",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": "地歴公民科",
                        "weight": "bold",
                        "size": "lg",
                        "align": "center",
                        "gravity": "center",
                        "contents": []
                    }
                    ]
                },
                "hero": {
                    "type": "image",
                    "url": "https://vos.line-scdn.net/bot-designer-template-images/bot-designer-icon.png",
                    "size": "xxs",
                    "aspectRatio": "1.51:1",
                    "aspectMode": "fit"
                },
                "body": {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "none",
                    "margin": "none",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "日A",
                        "text": "日本史Aについての質問"
                        },
                        "margin": "none"
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "日B",
                        "text": "日本史Bについての質問"
                        },
                        "margin": "none"
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "世A",
                        "text": "世界史Aについての質問"
                        },
                        "margin": "none"
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "世B",
                        "text": "世界史Bについての質問"
                        }
                    }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "地理",
                        "text": "地理についての質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "現社",
                        "text": "現代社会についての質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "政経",
                        "text": "政治経済についての質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "倫理",
                        "text": "倫理についての質問"
                        }
                    }
                    ]
                }
                }
            """
            flex_message_json_dict = json.loads(flex_message_json_string)
            line_bot_api.reply_message(event.reply_token,
            FlexSendMessage(alt_text='alt_text',contents=flex_message_json_dict))
    
    
    
        elif event.message.text == "英語についての質問" and user_list[name]["main_subject"] == "0":
            user_list[name]["main_subject"] = "英語"
            flex_message_json_string="""
                {
                "type": "bubble",
                "size": "mega",
                "direction": "ltr",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": "英語科",
                        "weight": "bold",
                        "size": "lg",
                        "align": "center",
                        "contents": []
                    }
                    ]
                },
                "hero": {
                    "type": "image",
                    "url": "https://vos.line-scdn.net/bot-designer-template-images/bot-designer-icon.png",
                    "size": "xxs",
                    "aspectRatio": "1.51:1",
                    "aspectMode": "fit"
                },
                "body": {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "C英Ⅰ",
                        "text": "コミュニケーション英語Ⅰについての質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "C英Ⅱ",
                        "text": "コミュニケーション英語Ⅱについての質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "C英Ⅲ",
                        "text": "コミュニケーション英語Ⅲについての質問"
                        }
                    }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "英表Ⅰ",
                        "text": "英語表現Ⅰについての質問"
                        }
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "英表Ⅱ",
                        "text": "英語表現Ⅱについての質問"
                        }
                    }
                    ]
                }
                }
            """
            flex_message_json_dict = json.loads(flex_message_json_string)
            line_bot_api.reply_message(event.reply_token,
            FlexSendMessage(alt_text='alt_text',contents=flex_message_json_dict))
    

        elif event.message.text in select and user_list[name]["subject"] == "0" and user_list[name]["main_subject"] != "0":
                ar_message = event.message.text
                xsubject= select[ar_message]
                user_list[name]["subject"] = xsubject 
                line_bot_api.reply_message(event.reply_token,TextSendMessage("質問項目は"+ xsubject +"についてでよろしいですか？\nよろしければ、はじめに”&question!”と打ってから質問をしてください。\nまた、質問項目を変えたい場合は”質問をやめる”と送って、はじめからやり直してください。"))

        elif "&question!" in event.message.text and user_list[name]["subject"] != "0" and user_list[name]["question"] == "0":
            quest = event.message.text
            user_list[name]["question"] = quest.replace('&question!', '')
            dm_text = user_list[name]["question"]
            send_subject = user_list[name]["subject"]
            number = datetime.datetime.now()
            s3 = boto3.resource('s3')
            file = str(number) + ".json"
            fp = open("/tmp/" + file , 'w')
            json.dump(user_list,fp,indent=4)
            fp.close() 
            s3.meta.client.upload_file("/tmp/" + file, 'push-go', file)
            os.remove("/tmp/" + file)
            line_bot_api.reply_message(event.reply_token,TextSendMessage("質問を受け付けました。\n 質問内容は以下の通りです。\n" + send_subject + dm_text))
            user_list[name]["main_subject"] = "0"
            user_list[name]["subject"] = "0"
            user_list[name]["question"] = "0" 
        
        elif event.message.text == "質問をやめる":
            user_list[name]["main_subject"] = "0" 
            user_list[name]["subject"] = "0"
            user_list[name]["question"] = "0"
            line_bot_api.reply_message(event.reply_token,TextSendMessage("質問をとりけしました。\n"))
    
        else:
            line_bot_api.reply_message(event.reply_token,
            TextSendMessage("正しく入力してください。\n困ったら”ヘルプ”と送ってください。"))
            

    
    try:
        handler.handle(body, signature)

            
    except LineBotApiError as e:
        logger.error("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            logger.error("  %s: %s" % (m.property, m.message))
        return error_json
        
    except InvalidSignatureError:
        return error_json

    return ok_json
    