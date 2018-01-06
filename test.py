import unittest
from app import game_info
from app import user_info
from app import app

class TestGameInfo(unittest.TestCase):

    def test_extract_name(self):
        app_id = "80"
        name = "Conter-Strike: Condition Zero"
        response_json = {
            app_id : {
                'success' : True,
                'data'      : {
                    'type':'game',
                    'name':name,
                    'steam_appid':int(app_id)
                }
           }
        }
        self.assertEqual(name, game_info.extract_name(response_json, app_id))

class TestUserInfo(unittest.TestCase):

    def test_url_constructor(self):
        self.assertEqual(
            'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001?format=json&steamid=12345&key=54321',
            user_info.owned_games_url(steamid=12345, apikey=54321)
        )

if __name__ == '__main__':
    unittest.main()
