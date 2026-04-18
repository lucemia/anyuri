剛剛發布了 anyuri — 一個從 GliaCloud 內部工具中抽取出來的 Python 套件。                                                                                                                                                    
                                                                                                                                                                                                                             
解決的問題很簡單，但非常煩人：當你的程式需要同時處理 GCS、S3、本地檔案和 HTTP URL，程式碼很容易變成這樣——                                                                                                                  
                                                                                                                                                                                                                             
# Before
def ffprobe(uri: str) -> Any:
    if uri.startswith("gs://") or uri.startswith("https://storage.googleapis.com/"):
        # convert to https ...
    elif uri.startswith("http://") or uri.startswith("https://"):
        ...
    elif uri.startswith("file://") or uri.startswith("/"):
        # convert to local path ...
    do_ffprobe(converted_uri)

# After
def ffprobe(uri: AnyUri) -> Any:
    do_ffprobe(uri.as_source())

                                      
另一個常見的頭痛問題：同一個 GCS 檔案同時有 gs://bucket/key 和 https://storage.googleapis.com/bucket/key 兩種表示方式，每次呼叫不同工具都要手動轉換。用 uri.as_source() 就搞定了，不用再寫任何判斷。
                                                                                                                                                                                                                             
而且 AnyUri 和 str 相容，可以直接丟進任何現有的程式碼，不需要改動其他地方。
                                                                                                                                                                                                                             
測試覆蓋率 96%，支援 Pydantic v1/v2，零強制依賴。               
                                                                                                                                                                                                                             
📦 pip install anyuri[all]                                                                                                                                                                                                 
📖 https://lucemia.github.io/anyuri/                                                                                                                                                                                       
🐙 https://github.com/lucemia/anyuri]

感謝我老婆 JuChing Peng 的支持與包容，