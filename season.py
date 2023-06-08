import requests
import numpy as np


class season:
    def __init__(self, seasonYear, loadMatchesIDS=True):
        self.seasonYear: str = seasonYear
        self.seasonid = self.getSeasonID()
        if loadMatchesIDS:
            self.matches_ids = self.getMatchesIDs()

    def build_bad_match_table(self, word):
        table = {}

        for i in range(len(word) - 1):
            table[word[i]] = len(word) - 1 - i

        return table

    def find_word_occurrences_boyer_moore_horspool(self, large_string, word):
        occurrences = []
        text_len = len(large_string)
        word_len = len(word)
        bad_match_table = self.build_bad_match_table(word)
        i = 0
        while i <= text_len - word_len:
            j = word_len - 1
            while j >= 0 and large_string[i + j] == word[j]:
                j -= 1
            if j == -1:
                occurrences.append(i)
                i += word_len
            else:
                char = large_string[i + j]
                i += bad_match_table.get(char, word_len)
        return occurrences

    def apiRequestToGetSeasonData(self):
        allSeasonData = ""
        for year in range(1, 14):
            url = f"https://global.lsapp.eu/12602/parent/602/x/feed/tse_1_1_{self.seasonid}_-"+str(year)
            payload = {}
            headers = {
              'X-Fsign': 'SW9D1eZo'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            allSeasonData += response.text
        return allSeasonData

    def getMatchesIDs(self):
        large_string = self.apiRequestToGetSeasonData()
        #this is a post-fix in the flashscore api to match ids 
        # any weird text like this is just a postfix to a targeted data 
        word = "¬AD÷"
        array_occurances_matches = self.find_word_occurrences_boyer_moore_horspool(large_string, word)
        matchesIDs = []
        for i in array_occurances_matches:
            id = large_string[i-8:i]

            matchesIDs.append(id)
        word = "¬FK÷"
        array_occurances_awayTeams = self.find_word_occurrences_boyer_moore_horspool(large_string, word)
        awayTeams = []
        for i in array_occurances_awayTeams:
            line_to_edit = large_string[i-30:i]
            start_index = line_to_edit.index("¬AF÷") + len("¬AF÷")
            awayTeams.append(line_to_edit[start_index:i])

        word = "¬FH÷"
        array_occurances_homeTeams = self.find_word_occurrences_boyer_moore_horspool(large_string, word)
        homeTeams = []
        for i in array_occurances_homeTeams:
            line_to_edit = large_string[i-30:i]
            start_index = line_to_edit.index("¬AE÷") + len("¬AE÷")
            homeTeams.append(line_to_edit[start_index:i])
        matchesData = {}
        for i, j, k in zip(homeTeams, awayTeams, matchesIDs):
            matchesData[i+" vs "+j] = k
        return matchesData

    def apiRequestToGetYearsData(self):
        url = "https://global.lsapp.eu/12602/parent/602/x/feed/tsi_6kJqdMr2"
        payload = {}
        headers = {
          'X-Fsign': 'SW9D1eZo',
          'User-Agent': 'okhttp/4.9.3'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        return response.text

    def getAllSeasonIDs(self):
        large_string = self.apiRequestToGetYearsData()
        word = "¬THT÷"
        yearsoccurances = self.find_word_occurrences_boyer_moore_horspool(large_string,word)
        yearsIDs = []
        for i in yearsoccurances:
            id = large_string[i-8:i]
            yearsIDs.append(id)

        return yearsIDs

    def getSeasonID(self):
        large_string = self.apiRequestToGetYearsData()
        year_occ = self.find_word_occurrences_boyer_moore_horspool(large_string, self.seasonYear)
        if year_occ:
            year_id = large_string[year_occ[0]+27:year_occ[0]+35]
        else:
            return None
        return year_id

    def getResults(self):
        """
        this function will scrape all the results of the season
        this function will output an numpy array for future calculation
        for exp like this
        [4 4 0 2 1]
        so the first match the home team scored 4
        and the first match the away team scored 4
        now the 0 will be the delimiter between matches
        so the second match the home team scored 2
        and the second match the away team scored 1
        """

        large_string = self.apiRequestToGetSeasonData()
        homeresults_occrances = self.find_word_occurrences_boyer_moore_horspool(large_string, "¬BA÷")
        awayresults_occrances = self.find_word_occurrences_boyer_moore_horspool(large_string, "¬BB÷")
        results = np.array([])
        for i, j in zip(homeresults_occrances, awayresults_occrances):
            """
             6 is refering to the case where there is more that 10 goals 
             so 2 for goals and 3 for ¬AG÷ or ¬AH÷ for the away
            """
            line_to_edit = large_string[i-6:i]
            start_index = line_to_edit.index("¬AG÷") + len("¬AG÷")
            homeresult = line_to_edit[start_index:i]

            line_to_edit = large_string[j-6:j]
            start_index = line_to_edit.index("¬AH÷") + len("¬AH÷")
            awayresult = line_to_edit[start_index:j]

            results = np.append(results, 0)
            results = np.append(results, int(homeresult))
            results = np.append(results, int(awayresult))
        return results[1:]



bestseason = season("2007/2008",False)
print(bestseason.seasonid)
array = bestseason.getResults()
print(array[:20])



