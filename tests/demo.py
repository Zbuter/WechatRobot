

import xml.etree.ElementTree as ET
import html

from wcferry import WxMsg

xml_data = '''
<msg>
    <appmsg appid="" sdkver="0">
        <title>4</title>
        <des />
        <action>view</action>
        <type>57</type>
        <showtype>0</showtype>
        <content />
        <url />
        <dataurl />
        <lowurl />
        <lowdataurl />
        <recorditem />
        <thumburl />
        <messageaction />
        <laninfo />
        <refermsg>
            <type>49</type>
            <svrid>770372943221382333</svrid>
            <fromusr>52347125927@chatroom</fromusr>
            <chatusr>zhangjiashun7758</chatusr>
            <createtime>1743646797</createtime>
            <msgsource>&lt;msgsource&gt;
    &lt;pua&gt;1&lt;/pua&gt;
    &lt;sec_msg_node&gt;
        &lt;uuid&gt;cd856dcb01b30ca7b0ec4b967e7b228d_&lt;/uuid&gt;
        &lt;risk-file-flag /&gt;
        &lt;risk-file-md5-list /&gt;
        &lt;alnode&gt;
            &lt;fr&gt;1&lt;/fr&gt;
        &lt;/alnode&gt;
    &lt;/sec_msg_node&gt;
&lt;/msgsource&gt;
</msgsource>
            <content>&lt;msg&gt;
    &lt;fromusername&gt;zhangjiashun7758&lt;/fromusername&gt;
    &lt;scene&gt;0&lt;/scene&gt;
    &lt;commenturl&gt;&lt;/commenturl&gt;
    &lt;appmsg appid="" sdkver="0"&gt;
        &lt;title&gt;3&lt;/title&gt;
        &lt;des&gt;&lt;/des&gt;
        &lt;action&gt;view&lt;/action&gt;
        &lt;type&gt;57&lt;/type&gt;
        &lt;showtype&gt;0&lt;/showtype&gt;
        &lt;content&gt;&lt;/content&gt;
        &lt;url&gt;&lt;/url&gt;
        &lt;dataurl&gt;&lt;/dataurl&gt;
        &lt;lowurl&gt;&lt;/lowurl&gt;
        &lt;lowdataurl&gt;&lt;/lowdataurl&gt;
        &lt;recorditem&gt;&lt;/recorditem&gt;
        &lt;thumburl&gt;&lt;/thumburl&gt;
        &lt;messageaction&gt;&lt;/messageaction&gt;
        &lt;laninfo&gt;&lt;/laninfo&gt;
        &lt;refermsg&gt;
            &lt;type&gt;49&lt;/type&gt;
            &lt;svrid&gt;5905862875530204560&lt;/svrid&gt;
            &lt;fromusr&gt;52347125927@chatroom&lt;/fromusr&gt;
            &lt;chatusr&gt;zhangjiashun7758&lt;/chatusr&gt;
            &lt;createtime&gt;1743646793&lt;/createtime&gt;
            &lt;msgsource&gt;&amp;lt;msgsource&amp;gt;
    &amp;lt;pua&amp;gt;1&amp;lt;/pua&amp;gt;
    &amp;lt;sec_msg_node&amp;gt;
        &amp;lt;uuid&amp;gt;189888576acc2f2ca648ce30c7ebe0c7_&amp;lt;/uuid&amp;gt;
        &amp;lt;risk-file-flag /&amp;gt;
        &amp;lt;risk-file-md5-list /&amp;gt;
        &amp;lt;alnode&amp;gt;
            &amp;lt;fr&amp;gt;1&amp;lt;/fr&amp;gt;
        &amp;lt;/alnode&amp;gt;
    &amp;lt;/sec_msg_node&amp;gt;
&amp;lt;/msgsource&amp;gt;
&lt;/msgsource&gt;
            &lt;content&gt;&amp;lt;msg&amp;gt;
    &amp;lt;fromusername&amp;gt;zhangjiashun7758&amp;lt;/fromusername&amp;gt;
    &amp;lt;scene&amp;gt;0&amp;lt;/scene&amp;gt;
    &amp;lt;commenturl&amp;gt;&amp;lt;/commenturl&amp;gt;
    &amp;lt;appmsg appid=&amp;quot;&amp;quot; sdkver=&amp;quot;0&amp;quot;&amp;gt;
        &amp;lt;title&amp;gt;2&amp;lt;/title&amp;gt;
        &amp;lt;des&amp;gt;&amp;lt;/des&amp;gt;
        &amp;lt;action&amp;gt;view&amp;lt;/action&amp;gt;
        &amp;lt;type&amp;gt;57&amp;lt;/type&amp;gt;
        &amp;lt;showtype&amp;gt;0&amp;lt;/showtype&amp;gt;
        &amp;lt;content&amp;gt;&amp;lt;/content&amp;gt;
        &amp;lt;url&amp;gt;&amp;lt;/url&amp;gt;
        &amp;lt;dataurl&amp;gt;&amp;lt;/dataurl&amp;gt;
        &amp;lt;lowurl&amp;gt;&amp;lt;/lowurl&amp;gt;
        &amp;lt;lowdataurl&amp;gt;&amp;lt;/lowdataurl&amp;gt;
        &amp;lt;recorditem&amp;gt;&amp;lt;/recorditem&amp;gt;
        &amp;lt;thumburl&amp;gt;&amp;lt;/thumburl&amp;gt;
        &amp;lt;messageaction&amp;gt;&amp;lt;/messageaction&amp;gt;
        &amp;lt;laninfo&amp;gt;&amp;lt;/laninfo&amp;gt;
        &amp;lt;refermsg&amp;gt;
            &amp;lt;type&amp;gt;1&amp;lt;/type&amp;gt;
            &amp;lt;svrid&amp;gt;1535974403122534616&amp;lt;/svrid&amp;gt;
            &amp;lt;fromusr&amp;gt;52347125927@chatroom&amp;lt;/fromusr&amp;gt;
            &amp;lt;chatusr&amp;gt;zhangjiashun7758&amp;lt;/chatusr&amp;gt;
            &amp;lt;createtime&amp;gt;1743646786&amp;lt;/createtime&amp;gt;
            &amp;lt;msgsource&amp;gt;&amp;amp;lt;msgsource&amp;amp;gt;
    &amp;amp;lt;sec_msg_node&amp;amp;gt;
        &amp;amp;lt;alnode&amp;amp;gt;
            &amp;amp;lt;fr&amp;amp;gt;1&amp;amp;lt;/fr&amp;amp;gt;
        &amp;amp;lt;/alnode&amp;amp;gt;
    &amp;amp;lt;/sec_msg_node&amp;amp;gt;
    &amp;amp;lt;pua&amp;amp;gt;1&amp;amp;lt;/pua&amp;amp;gt;
&amp;amp;lt;/msgsource&amp;amp;gt;
&amp;lt;/msgsource&amp;gt;
            &amp;lt;content&amp;gt;1&amp;lt;/content&amp;gt;
        &amp;lt;/refermsg&amp;gt;
        &amp;lt;extinfo&amp;gt;&amp;lt;/extinfo&amp;gt;
        &amp;lt;sourceusername&amp;gt;&amp;lt;/sourceusername&amp;gt;
        &amp;lt;sourcedisplayname&amp;gt;&amp;lt;/sourcedisplayname&amp;gt;
        &amp;lt;commenturl&amp;gt;&amp;lt;/commenturl&amp;gt;
        &amp;lt;appattach&amp;gt;
            &amp;lt;totallen&amp;gt;0&amp;lt;/totallen&amp;gt;
            &amp;lt;attachid&amp;gt;&amp;lt;/attachid&amp;gt;
            &amp;lt;emoticonmd5&amp;gt;&amp;lt;/emoticonmd5&amp;gt;
            &amp;lt;fileext&amp;gt;&amp;lt;/fileext&amp;gt;
            &amp;lt;aeskey&amp;gt;&amp;lt;/aeskey&amp;gt;
        &amp;lt;/appattach&amp;gt;
        &amp;lt;webviewshared&amp;gt;
            &amp;lt;publisherId&amp;gt;&amp;lt;/publisherId&amp;gt;
            &amp;lt;publisherReqId&amp;gt;0&amp;lt;/publisherReqId&amp;gt;
        &amp;lt;/webviewshared&amp;gt;
        &amp;lt;weappinfo&amp;gt;
            &amp;lt;pagepath&amp;gt;&amp;lt;/pagepath&amp;gt;
            &amp;lt;username&amp;gt;&amp;lt;/username&amp;gt;
            &amp;lt;appid&amp;gt;&amp;lt;/appid&amp;gt;
            &amp;lt;appservicetype&amp;gt;0&amp;lt;/appservicetype&amp;gt;
        &amp;lt;/weappinfo&amp;gt;
        &amp;lt;websearch /&amp;gt;
    &amp;lt;/appmsg&amp;gt;
    &amp;lt;appinfo&amp;gt;
        &amp;lt;version&amp;gt;1&amp;lt;/version&amp;gt;
        &amp;lt;appname&amp;gt;Window wechat&amp;lt;/appname&amp;gt;
    &amp;lt;/appinfo&amp;gt;
&amp;lt;/msg&amp;gt;
&lt;/content&gt;
        &lt;/refermsg&gt;
        &lt;extinfo&gt;&lt;/extinfo&gt;
        &lt;sourceusername&gt;&lt;/sourceusername&gt;
        &lt;sourcedisplayname&gt;&lt;/sourcedisplayname&gt;
        &lt;commenturl&gt;&lt;/commenturl&gt;
        &lt;appattach&gt;
            &lt;totallen&gt;0&lt;/totallen&gt;
            &lt;attachid&gt;&lt;/attachid&gt;
            &lt;emoticonmd5&gt;&lt;/emoticonmd5&gt;
            &lt;fileext&gt;&lt;/fileext&gt;
            &lt;aeskey&gt;&lt;/aeskey&gt;
        &lt;/appattach&gt;
        &lt;webviewshared&gt;
            &lt;publisherId&gt;&lt;/publisherId&gt;
            &lt;publisherReqId&gt;0&lt;/publisherReqId&gt;
        &lt;/webviewshared&gt;
        &lt;weappinfo&gt;
            &lt;pagepath&gt;&lt;/pagepath&gt;
            &lt;username&gt;&lt;/username&gt;
            &lt;appid&gt;&lt;/appid&gt;
            &lt;appservicetype&gt;0&lt;/appservicetype&gt;
        &lt;/weappinfo&gt;
        &lt;websearch /&gt;
    &lt;/appmsg&gt;
    &lt;appinfo&gt;
        &lt;version&gt;1&lt;/version&gt;
        &lt;appname&gt;Window wechat&lt;/appname&gt;
    &lt;/appinfo&gt;
&lt;/msg&gt;
</content>
            <displayname>改个名字11</displayname>
        </refermsg>
        <extinfo />
        <sourceusername />
        <sourcedisplayname />
        <commenturl />
        <appattach>
            <totallen>0</totallen>
            <attachid />
            <emoticonmd5 />
            <fileext />
            <aeskey />
        </appattach>
        <webviewshared>
            <publisherId />
            <publisherReqId>0</publisherReqId>
        </webviewshared>
        <weappinfo>
            <pagepath />
            <username />
            <appid />
            <appservicetype>0</appservicetype>
        </weappinfo>
        <websearch />
    </appmsg>
    <fromusername>zhangjiashun7758</fromusername>
    <scene>0</scene>
    <appinfo>
        <version>1</version>
        <appname></appname>
    </appinfo>
    <commenturl></commenturl>
</msg>'''

# 解析XML数据
root = ET.fromstring(xml_data)


# 定义一个递归函数来查找所有refermsg元素
refs = []
msg:WxMsg = None
def find_refermsgs(element):

    refermsg = element.find('.//refermsg')
    if refermsg is None:
        return None
    content = refermsg.find("./content")
    msg.sender = content.find('./fromusername')
    appmsg = content.find('./appmsg')
    msg.content = appmsg.find('./title')
    msg.type = appmsg.find('./type')
    msg.roomid = appmsg.find


    pass

    return refs

def parse_refmsg(source):
    refermsgs = source.findall('.//refermsg')


# 调用递归函数并打印结果
refermsgs = find_refermsgs(root)
for refermsg in refermsgs:
    print(refermsg)


