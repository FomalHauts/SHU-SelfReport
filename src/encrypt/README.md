# 加密



```javascript
// main.js
window.jiami = function(e) {
​    var n = new JSEncrypt;
​    n.setPublicKey("-----BEGIN PUBLIC KEY-----\n        MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDl/aCgRl9f/4ON9MewoVnV58OL\n        OU2ALBi2FKc5yIsfSpivKxe7A6FitJjHva3WpM7gvVOinMehp6if2UNIkbaN+plW\n        f5IwqEVxsNZpeixc4GsbY9dXEk3WtRjwGSyDLySzEESH/kpJVoxO7ijRYqU+2oSR\n        wTBNePOk1H+LRQokgQIDAQAB\n        -----END PUBLIC KEY-----");
​    for (var s = 0; s < e.length; s++) {
​        var t = n.encrypt($("#" + e[s])[0].value);
​        document.getElementsByName(e[s])[0].value = t
​    }
}
```

在main.js中设置加密函数jiami,利用jsencrypt.js生成JSEncrypt对象，设置公钥，并对密码加密后，取其[0]下标，并将密码设置为加密后的数据。

```javascript
// login.js
"use strict";
$(document).ready(function() {
    window.button_name = ["登录", "Login"];
    var e = $("#submit")
      , i = $("#select_language")
      , a = i18next.store.data;
    e.on("click", function() {
        var n = $(".from_input");
        if ("正在登录...请稍后" === e[0].innerText && "Signing in... Please wait" === e[0].innerText)
            return !1;
        for (var t = 0; t < n.length; t++)
            if (!n[t].value)
                return tip_notice(a.cn.translation.message.public.emptyForm, a.us.translation.message.public.emptyForm),
                !1;
        window.jiami(["password"]),
        e.css("background", "#6d6d6d"),
        "中文" === i.val() ? e.text("正在登录...请稍后") : e.text("Signing in... Please wait")
    })
});

```

Login.js判断用户点击事件，并对密码进行加密。