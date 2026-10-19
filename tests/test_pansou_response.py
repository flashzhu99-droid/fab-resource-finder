import unittest
from cloud.pansou_bridge import unpack_response, count_upstream_links, convert
class TestPanSouResponse(unittest.TestCase):
 def test_wrapped(self):
  payload={"code":0,"data":{"merged_by_type":{"baidu":[{"url":"https://pan.baidu.com/s/1abcdefgh","work_title":"超纯水系统维护手册"}]}}}
  self.assertEqual(count_upstream_links(payload),1)
  self.assertEqual(len(convert(payload,"超纯水")),1)
 def test_direct_provider_map(self):
  sample={"baidu":[{"url":"https://pan.baidu.com/s/1abcdefgh","work_title":"超纯水系统维护手册"}],"quark":[]}
  self.assertEqual(count_upstream_links({"data":sample}),1)
  self.assertEqual(len(convert({"data":sample},"超纯水")),1)
 def test_unwrapped(self):
  self.assertEqual(count_upstream_links({"merged_by_type":{"quark":[]}}),0)
 def test_unknown_schema(self):
  with self.assertRaises(ValueError):convert({"code":0,"data":{"results":[]}},"超纯水")
 def test_unrelated(self):
  payload={"code":0,"data":{"merged_by_type":{"baidu":[{"url":"https://pan.baidu.com/s/1abcdefgh","work_title":"Fab Four Beatles music"}]}}}
  self.assertEqual(len(convert(payload,"FAB")),0)
if __name__=="__main__":unittest.main()
