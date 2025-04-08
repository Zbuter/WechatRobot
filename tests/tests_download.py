content = '''<msg><emoji fromusername="wxid_zb6ns68nyxm822" tousername="53354824920@chatroom" type="3" idbuffer="media:0_0" md5="4da80c010a4981860b3c97a31f7f676a" len="22998" productid="" androidmd5="4da80c010a4981860b3c97a31f7f676a" androidlen="22998" s60v3md5="4da80c010a4981860b3c97a31f7f676a" s60v3len="22998" s60v5md5="4da80c010a4981860b3c97a31f7f676a" s60v5len="22998" cdnurl="http://vweixinf.tc.qq.com/110/20401/stodownload?m=4da80c010a4981860b3c97a31f7f676a&amp;filekey=3043020101042f302d02016e0402534804203464613830633031306134393831383630623363393761333166376636373661020259d6040d00000004627466730000000132&amp;hy=SH&amp;storeid=267e6825400026ac76341e3190000006e01004fb15348277ef17157ae1701d&amp;ef=1&amp;bizid=1022" designerid="" thumburl="" encrypturl="http://vweixinf.tc.qq.com/110/20402/stodownload?m=cccfbc59d77f7af5bf80625ec6a22363&amp;filekey=3043020101042f302d02016e0402534804206363636662633539643737663761663562663830363235656336613232333633020259e0040d00000004627466730000000132&amp;hy=SH&amp;storeid=267e6825400034f586341e3190000006e02004fb25348277ef17157ae1703a&amp;ef=2&amp;bizid=1022" aeskey="aa44d0aae61e4d5d832ac92315969a9d" externurl="http://vweixinf.tc.qq.com/110/20403/stodownload?m=72919a4e5d6e719ae57f848ab6f5e2f3&amp;filekey=3043020101042f302d02016e040253480420373239313961346535643665373139616535376638343861623666356532663302023600040d00000004627466730000000132&amp;hy=SH&amp;storeid=267e682540003e7ea6341e3190000006e03004fb35348277ef17157ae17046&amp;ef=3&amp;bizid=1022" externmd5="60d99dc6c5d30be02e62707b708d08df" width="226" height="212" tpurl="" tpauthkey="" attachedtext="" attachedtextcolor="" lensid="" emojiattr="" linkid="" desc=""></emoji><gameext type="0" content="0"></gameext><extcommoninfo></extcommoninfo></msg>'''

import xml.etree.ElementTree as ET
import requests
def identify_image_format(file_b):
    if file_b.startswith(b'\xff\xd8'):
        return 'jpg'
    elif file_b.startswith(b'\x89PNG'):
        return 'png'
    elif file_b.startswith(b'GIF8'):
        return 'gif'
    elif file_b.startswith(b'BM'):
        return 'bmp'
    elif file_b.startswith(b'II*') or file_b.startswith(b'MM\x00*'):
        # TIFF可以是'II*'（Big-endian）或'MM\x00*'（Little-endian，注意MM后的\x00）
        # 但'MM\x00*'的前两个字节实际上是'MM'，所以我们需要检查这四个字节
        if file_b[:4] == b'MM\x00*':
            return 'tiff'
        elif file_b[:4] == b'II*':
            return 'tiff'
        # 否则，如果只有'MM'或'II'，我们可能需要进一步检查
    elif file_b.startswith(b'RIFF') and file_b[8:12] in (b'WEBP',):
        # WebP文件以RIFF开头，但我们需要检查接下来的四个字节是否为'WEBP'
        return 'webp'
    else:
        return None


if __name__ == '__main__':
    content = ET.fromstring(content)
    emoji = content.find('./emoji')
    url = emoji.attrib['cdnurl']
    resp = requests.get(url)
    content = resp.content
    suffix = identify_image_format(resp.content)
    with open('./image.'+suffix, 'wb') as f:
        f.write(content)

    pass