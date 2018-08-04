import unittest
import chelsea_bot


class TestBot(unittest.TestCase):

    def setUp(self):
        self.text = "Willian returns to training following passport issue amid Real Madrid interest as Chelsea are put through their paces ahead of their Community Shield clash against Manchester City."
        self.text2 = "Chelsea aim to hijack Tottenham deal for Jack Grealish as they eye late swoop for Aston Villa's £20m star."
        self.text3 = "'He will stay with us': Chelsea boss Maurizio Sarri confirms teenager Callum Hudson-Odoi will be handed first-team chance this season."
        self.text4 = "Willian returns to training as Chelsea stars are put through their paces ahead of Community Shield clash against Manchester City."
        self.text5 = "'He's on the radar': Mason Mount to be tracked by England while on loan from Chelsea at Derby, says Frank Lampard."

        self.text_list_true = [self.text3.split(), self.text2.split(), self.text4.split(), self.text5.split()]
        self.text_list_false = [self.text2.split(), self.text3.split(), self.text4.split(), self.text.split(), self.text5.split()]

    def test_same_text_true(self):
        result = chelsea_bot.same_text(self.text_list_true, self.text)
        self.assertEqual(result, True)

    def test_same_text_false(self):
        result = chelsea_bot.same_text(self.text_list_false, self.text)
        self.assertEqual(result, False)

if __name__ == '__main__':
    unittest.main()