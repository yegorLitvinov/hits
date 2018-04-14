def serialize_user_agent(ua):
    return {
        'browser': {
            'family': ua.browser.family,
            'version': ua.browser.version,
            'version_string': ua.browser.version_string,
        },
        'os': {
            'family': ua.os.family,
            'version': ua.os.version,
            'version_string': ua.os.version_string,
        },
        'device': {
            'family': ua.device.family,
            'brand': ua.device.brand,
            'model': ua.device.model,
        },
        'is_bot': ua.is_bot,
        'is_email_client': ua.is_email_client,
        'is_mobile': ua.is_mobile,
        'is_pc': ua.is_pc,
        'is_tablet': ua.is_tablet,
        'is_touch_capable': ua.is_touch_capable,
        'ua_string': ua.ua_string,
    }
