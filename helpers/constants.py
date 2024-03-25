from typing import Final, Dict

BASE_URL: Final[str] = "https://api.twitter.com/1.1/onboarding/task.json"

FLOW_INIT_PARAMS: Final[Dict[str, str]] = {
    "api_version": "2",
    "ext": "highlightedLabel,mediaColor",
    "flow_name": "welcome",
    "include_entities": "1",
    "include_profile_interstitial_type": "true",
    "include_profile_location": "true",
    "include_user_entities": "true",
    "include_user_hashtag_entities": "true",
    "include_user_mention_entities": "true",
    "include_user_symbol_entities": "true",
    "known_device_token": "",
    "sim_country_code": "GB",
}

FLOW_INIT_PAYLOAD: Final[Dict] = {
    "component_versions": {
        "spacer": 1,
        "progress_indicator": 1,
        "settings_group": 1,
        "card_wrapper": 1,
        "image": 1,
        "action": 1,
        "button": 1,
        "inline_callout": 1,
        "button_item": 1,
        "precise_location": 1,
        "tweet": 1,
        "inline_feedback": 1,
        "inline_tooltip": 1,
        "user": 1,
        "list": 1,
        "destructive_action": 1,
        "static_text": 1,
        "alert_example": 1,
        "boolean": 1,
        "info_item": 1,
        "toggle_wrapper": 1,
    },
    "input_flow_data": {
        "flow_context": {"start_location": {"location": "splash_screen"}}
    },
    "subtask_versions": {
        "enter_date": 1,
        "sign_up": 2,
        "enter_username": 3,
        "alert_dialog": 1,
        "choice_selection": 6,
        "privacy_options": 1,
        "user_recommendations_list": 5,
        "upload_media": 1,
        "tweet_selection_urt": 1,
        "action_list": 2,
        "update_users": 1,
        "select_banner": 2,
        "js_instrumentation": 1,
        "standard": 1,
        "settings_list": 7,
        "app_locale_update": 1,
        "open_home_timeline": 1,
        "generic_urt": 3,
        "wait_spinner": 3,
        "menu_dialog": 1,
        "open_account": 2,
        "single_sign_on": 1,
        "open_external_link": 1,
        "select_avatar": 4,
        "enter_password": 6,
        "cta": 7,
        "open_link": 1,
        "user_recommendations_urt": 4,
        "show_code": 1,
        "location_permission_prompt": 2,
        "sign_up_review": 5,
        "in_app_notification": 1,
        "security_key": 3,
        "phone_verification": 5,
        "contacts_live_sync_permission_prompt": 3,
        "check_logged_in_account": 1,
        "enter_phone": 2,
        "enter_text": 5,
        "enter_email": 2,
        "web_modal": 2,
        "notifications_permission_prompt": 4,
        "end_flow": 1,
        "alert_dialog_suppress_client_events": 1,
        "email_verification": 3,
    },
}

GENERAL_PARAMS: Final[Dict] = {
    "ext": "highlightedLabel,mediaColor",
    "include_entities": "1",
    "include_profile_interstitial_type": "true",
    "include_profile_location": "true",
    "include_user_entities": "true",
    "include_user_hashtag_entities": "true",
    "include_user_mention_entities": "true",
    "include_user_symbol_entities": "true",
}

PHONE_CODE_PAYLOAD: Final[Dict] = {
    "flow_token": "",
    "subtask_inputs": [
        {
            "subtask_id": "SplashScreenWithSso",
            "cta": {"link": "signup", "component_values": []},
        },
        {
            "subtask_id": "WelcomeFlowStartSignupOpenLink",
            "open_link": {"link": "welcome_flow_start_signup", "component_values": []},
        },
        {
            "subtask_id": "Signup",
            "sign_up": {
                "link": "next_link",
                "js_instrumentation": {"response": ""},
                "birthday": {"year": "", "month": "", "day": ""},
                "name": "",
                "phone_number": "",
            },
        },
        {
            "subtask_id": "ArkosePhone",
            "web_modal": {
                "completion_deeplink": 'twitter://onboarding/web_modal/next_link?access_token=captchatokenhere"',
                "link": "signup_with_phone_next_link",
            },
        },
        {
            "subtask_id": "SignupSettingsListPhoneNonEU",
            "settings_list": {
                "link": "next_link",
                "component_values": [],
                "setting_responses": [
                    {
                        "key": "twitter_for_web",
                        "response_data": {"boolean_data": {"result": "false"}},
                    }
                ],
            },
        },
        {
            "subtask_id": "SignupReview",
            "sign_up_review": {
                "link": "signup_with_phone_next_link",
                "component_values": [],
            },
        },
        {
            "subtask_id": "PhoneVerificationAlert",
            "alert_dialog": {"link": "next_link", "component_values": []},
        },
        {
            "subtask_id": "PhoneVerification",
            "phone_verification": {
                "code": "",
                "component_values": [],
                "by_voice": "false",
                "normalized_phone": "",
                "link": "next_link",
            },
        },
    ],
}

EMAIL_CODE_PAYLOAD: Final[Dict] = {
    "flow_token": None,
    "subtask_inputs": [
        {
            "subtask_id": "SplashScreenWithSso",
            "cta": {"link": "signup", "component_values": []},
        },
        {
            "subtask_id": "WelcomeFlowStartSignupOpenLink",
            "open_link": {"link": "welcome_flow_start_signup", "component_values": []},
        },
        {
            "subtask_id": "Signup",
            "sign_up": {
                "email": None,
                "js_instrumentation": {"response": None},
                "name": None,
                "birthday": {"year": None, "month": None, "day": None},
                "link": "email_next_link",
            },
        },
        {
            "subtask_id": "ArkoseEmail",
            "web_modal": {
                "completion_deeplink": 'twitter://onboarding/web_modal/next_link?access_token=captchatokenhere"',
                "link": "signup_with_email_next_link",
            },
        },
        {
            "subtask_id": "SignupSettingsListEmailNonEU",
            "settings_list": {
                "link": "next_link",
                "component_values": [],
                "setting_responses": [
                    {
                        "key": "twitter_for_web",
                        "response_data": {"boolean_data": {"result": "false"}},
                    }
                ],
            },
        },
        {
            "subtask_id": "SignupReview",
            "sign_up_review": {
                "link": "signup_with_email_next_link",
                "component_values": [],
            },
        },
        {
            "subtask_id": "EmailVerification",
            "email_verification": {
                "code": None,
                "component_values": [],
                "email": None,
                "link": "next_link",
            },
        },
    ],
}

PASSWORD_FLOW_PAYLOAD: Final[Dict] = {
    "flow_token": None,
    "subtask_inputs": [
        {
            "subtask_id": "EnterPassword",
            "enter_password": {"password": None, "link": "next_link"},
        }
    ],
}

AVATAR_FLOW_PAYLOAD: Final[Dict] = {
    "flow_token": None,
    "subtask_inputs": [
        {
            "subtask_id": "OpenAccount",
            "open_account": {"link": "next_link", "component_values": []},
        },
        {
            "subtask_id": "WelcomeFlowStartAccountSetupOpenLink",
            "open_link": {
                "link": "welcome_flow_start_account_setup",
                "component_values": [],
            },
        },
        {
            "subtask_id": "SelectAvatar",
            "select_avatar": {"link": "next_link", "component_values": []},
        },
        {
            "subtask_id": "UploadMedia",
            "upload_media": {"link": "next_link", "component_values": []},
        },
    ],
}

BIO_FLOW_PAYLOAD: Final[Dict] = {
    "flow_token": None,
    "subtask_inputs": [
        {
            "subtask_id": None,
            "enter_text": {
                "link": "skip_link",
                "component_values": [],
            },
        }
    ],
}

USERNAME_FLOW_PAYLOAD: Final[Dict] = {
    "flow_token": None,
    "subtask_inputs": [
        {
            "subtask_id": None,
            "enter_username": {"link": "next_link", "username": None},
        }
    ],
}

NOTIFICATION_FLOW_PAYLOAD: Final[Dict] = {
    "flow_token": None,
    "subtask_inputs": [
        {
            "subtask_id": None,
            "notifications_permission_prompt": {
                "link": "skip_link",
                "component_values": [],
            },
        }
    ],
}

PERMISSION_FLOW_PAYLOAD: Final[Dict] = {
    "flow_token": None,
    "subtask_inputs": [
        {
            "subtask_id": None,
            "contacts_live_sync_permission_prompt": {
                "link": "skip_link",
                "component_values": [],
            },
        }
    ],
}

LANGUAGE_FLOW_PAYLOAD: Final[Dict] = {
    "flow_token": None,
    "subtask_inputs": [
        {
            "subtask_id": None,
            "settings_list": {
                "setting_responses": [
                    {"key": "en", "response_data": {"boolean_data": {"result": True}}},
                    {"key": "fr", "response_data": {"boolean_data": {"result": True}}},
                    {"key": "am", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "ar", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "hy", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "eu", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "bn", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "my", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "bg", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "ca", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "cs", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "zh", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "ko", "response_data": {"boolean_data": {"result": False}}},
                    {
                        "key": "ckb",
                        "response_data": {"boolean_data": {"result": False}},
                    },
                    {"key": "da", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "dv", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "he", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "eo", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "et", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "fi", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "cy", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "ka", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "ja", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "el", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "gu", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "ht", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "hi", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "id", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "en", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "is", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "kn", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "km", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "lo", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "lv", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "lt", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "ml", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "ms", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "mr", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "ne", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "no", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "or", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "nl", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "ps", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "fa", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "pl", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "pt", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "pa", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "ro", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "ru", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "sr", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "sd", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "si", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "sl", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "es", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "sv", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "tl", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "ta", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "de", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "te", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "th", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "bo", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "tr", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "uk", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "ug", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "hu", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "ur", "response_data": {"boolean_data": {"result": False}}},
                    {"key": "vi", "response_data": {"boolean_data": {"result": False}}},
                    {
                        "key": "other",
                        "response_data": {"boolean_data": {"result": False}},
                    },
                ],
                "link": "next_link",
            },
        }
    ],
}
