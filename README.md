# adsl-proxy-server

# 开发说明
*  本项目使用py2exe打包，开发和运行于Win32下；
*  依赖项在requirements.txt中，可以使用Windows下的pip安装；
*  打包后在dist目录生成的rasapi32.dll与rasman.dll请删掉（因为这两个动态链接库文件是打包时平台的文件，Windows中包含了，无需
也无法移植到其他Windows版本）  


## 打包方法：
    python setup.py py2exe



## 使用方法
    编辑config.ini文件可以看到配置项，下面为配置项含义：
        DIALNAME-宽带连接名称
        ACCOUNT-宽带连接账号
        PASSWORD-宽带连接密码
        NODE_NAME-节点名称（如果部署到多台，请勿重名）
        PORT-代理端口号
        HTTP_CHANGE_STATUS_API-接口地址HOST部分  

    配置好以后执行server.exe便可以启动代理服务，端口号为配置文件中定义的PORT，IP地址会通过配置文件中指定的接口更新到代理库服务；
    客户端使用/get?type=dynamic_http拿到最新的动态代理服务器地址。
    程序通过调用/report?type=dynamic_http&ip=&port= 告知代理服务应该向ADSL服务端发送SHOULD_UPDATE!命令，从而ADSL服务端进行重连换IP的操作
