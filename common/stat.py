"""程序逻辑中的状态码"""

OK = 0
VCODE_ERR = 1000        #验证码发送失败
INVILD_VCODE = 1001     #验证码无效
ACCESS_TOKEN_ERR = 1002 #授权码接口错误
USER_INFO_ERR = 1003    #用户信息接口错误
LOGIN_REQUIRED = 1004   #用户未登录
USER_DATA_ERR = 1005    #用户数据错误
PROFILE_DATA_ERR = 1006 #用户交友资料数据错误