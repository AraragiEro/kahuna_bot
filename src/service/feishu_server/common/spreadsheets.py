import time

from . import api
from .client_utils import FeishuException
from .client_utils import (excol,
                           get_sheet_id_by_name,
                           create_sheet_request_data,
                           delete_sheet_request_data)
from ...log_server import logger

ANYONE_READABLE = "anyone_readable"

class DocPermission:
    _external_access_entity = ""
    _security_entity = ""
    _comment_entity = ""
    _share_entity = ""
    _manage_collaborator_entity = ""
    _link_share_entity = ""
    _copy_entity = ""

    def __init__(self, client, type: str, token: str):
        self.client = client
        self.type = type
        self.token = token
        self.init()

    def init(self):
        per_res = api.get_drive_v2_permissions_token_public(
            self.client.access_token, self.token, self.type
        )
        """example:
        {
          "external_access_entity": "open",
          "security_entity": "anyone_can_view",
          "comment_entity": "anyone_can_view",
          "share_entity": "anyone",
          "manage_collaborator_entity": "collaborator_can_view",
          "link_share_entity": "anyone_readable",
          "copy_entity": "anyone_can_view"
        }
        """
        per_res = per_res['data']['permission_public']
        self._external_access_entity = per_res['external_access_entity']
        self._security_entity = per_res['security_entity']
        self._comment_entity = per_res['comment_entity']
        self._share_entity = per_res['share_entity']
        self._manage_collaborator_entity = per_res['manage_collaborator_entity']
        self._link_share_entity = per_res['link_share_entity']
        self._copy_entity = per_res['copy_entity']

    @property
    def link_share_entity(self):
        return self._link_share_entity
    @link_share_entity.setter
    def link_share_entity(self, value):
        data = {
            "link_share_entity": value
        }
        res = api.patch_drive_v2_permissions_public(self.client.access_token, self.token, self.type,  data)
        if res:
            self._link_share_entity = value

class Sheet:
    client = None
    sheet_token = None
    sheet_id = None
    _title = None
    _url = None

    def __init__(self, client, sheet_token, sheet_id, url):
        self.client = client
        self.sheet_token = sheet_token
        self.sheet_id = sheet_id
        self._url = url

        self.init_by_token()

    @property
    def url(self):
        return f'{self._url}?sheet={self.sheet_id}'

    def init_by_token(self):
        sheet_info_res = api.get_sheets_v3_spreadsheets_spreadsheet_token_sheets_sheet_id(
                            self.client.access_token, self.sheet_token, self.sheet_id)

        if not sheet_info_res:
            raise FeishuException("getsheet info failed, create sheets failed.")
        self._title = sheet_info_res['data']['sheet']['title']

    def get_grid(self):
        res_data = api.get_sheets_v3_spreadsheets_spreadsheetToken_sheets_sheetId(
            self.client.access_token, self.sheet_token, self.sheet_id
        )

        return res_data['data']['sheet']['grid_properties']['column_count'], \
               res_data['data']['sheet']['grid_properties']['row_count']

    def delete(self):
        delete_request_data = delete_sheet_request_data(self.sheet_id)

        delete_res = api.post_sheets_v2_spreadsheets_spreadsheet_token_sheets_batch_update(
            self.client.access_token, self.sheet_token, delete_request_data
        )
        return delete_res

    def set_value(self, position: list[int, int], values: list[list]):
        x1 = position[0]
        y1 = position[1]

        if len(values) == 0:
            return None

        x2 = x1 + len(values[0]) - 1
        y2 = y1 + len(values) - 1

        data = {
            "valueRange": {
                "range": f"{self.sheet_id}!{excol(x1)}{y1}:{excol(x2)}{y2}",
                "values": values
            }
        }

        return api.put_sheets_v2_spreadsheets_values(self.client.access_token, self.sheet_token, data)

    def set_format(self, position: list[int, int], range: list[int, int], format_dict):
        x1 = position[0]
        y1 = position[1]

        x2 = x1 + range[0] - 1
        y2 = y1 + range[1] - 1

        data = {
            'appendStyle': {
                'range': f'{self.sheet_id}!{excol(x1)}{y1}:{excol(x2)}{y2}',
                'style': format_dict
            }
        }

        return api.put_sheets_v2_spreadsheets_spreadsheetToken_style(self.client.access_token, self.sheet_token, data)

    def set_dimension(self, start_index, end_index, dimension_type="ROWS", visible=True, fixed_size=130):

        data = {
            "dimension":{
                "sheetId": self.sheet_id,
                "majorDimension": dimension_type,
                "startIndex":start_index,
                "endIndex":end_index
            },
            "dimensionProperties":{
                "visible": visible,
                "fixedSize": fixed_size
            }
        }

        return api.put_sheets_v2_spreadsheets_spreadsheetToken_dimension_range(self.client.access_token, self.sheet_token, data)

    def clear_sheet(self):
        sheet_co, sheet_row = self.get_grid()
        empty_data = [["" for _ in range(sheet_co)] for _ in range(sheet_row)]

        return self.set_value([1, 1], empty_data)

class Spreadsheets:
    client = None
    sheet_token = None
    _title = None
    _url = None

    def __init__(self, client, sheet_token):
        self.client = client
        self.sheet_token = sheet_token
        self.init_by_token()
        self.permission = DocPermission(client, "sheet", sheet_token)

    @property
    def title(self):
        return self._title
    @title.setter
    def title(self, value):
        res = api.patch_sheets_v3_spreadsheets(self.client.access_token, self.sheet_token, value)
        if res:
            self._title = value
        else:
            logger.error("set title failed.")

    @property
    def url(self):
        return self._url

    def init_by_token(self):
        spwdsheet_info_res = api.get_sheets_v3_spreadsheets(self.client.access_token, self.sheet_token)

        if not spwdsheet_info_res:
            raise FeishuException("get_query_faild, create spreadsheets failed.")

        self._title = spwdsheet_info_res['data']['spreadsheet']['title']
        self._url = spwdsheet_info_res['data']['spreadsheet']['url']

    def get_sheet(self, sheet_name: str) -> Sheet:
        sheet_id = get_sheet_id_by_name(self.client.access_token, self.sheet_token, sheet_name)
        sheet = Sheet(self.client, self.sheet_token, sheet_id, self.url)

        return sheet

    def create_sheet(self, sheet_name: str, ignore_exist: bool = False) -> Sheet:
        if not ignore_exist:
            try:
                return self.get_sheet(sheet_name)
            except:
                pass

        create_request_data = create_sheet_request_data(sheet_name)
        create_res = api.post_sheets_v2_spreadsheets_spreadsheet_token_sheets_batch_update(
            self.client.access_token, self.sheet_token, create_request_data
        )
        sheet_id = create_res['data']['replies'][0]['addSheet']['properties']['sheetId']
        return Sheet(self.client, self.sheet_token, sheet_id, self.url)
