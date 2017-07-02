#!/usr/local/bin/python
''' Gathers textual representations of several numbers. See main part. '''
import time
import os
import urllib2
import json
from pyquery import PyQuery # easy_install PyQuery


class HelyesirasAPI(object):
    ''' Class to interact with an API that tranlates numbers to text. '''
    api_requests = 0

    results = {}

    def get_number(self, number):
        ''' Returns the textual representaion of a number given as a string.
        Examples: '0' -> 'nulla', '1' -> 'egy'
        '''
        if number in self.results:
            return self.results[number]
        else:
            self.results[number] = []

        # could not find any documentation about their API
        # let's use html, parse, then extract required information
        url = 'http://helyesiras.mta.hu/helyesiras/default/numerals?q=' + number
        response = urllib2.urlopen(url)
        self.api_requests = self.api_requests + 1

        if self.api_requests % 5 == 0:
            print self.api_requests
        if self.api_requests % 100 == 0:
            # be mindful of API overloads
            time.sleep(1)

        html = response.read()
        #print html
        query = PyQuery(html)
        #<ul class="result"><li>
        #print query
        tag = query('ul.result > li')
        for li_element in tag:
            # clean up the li tag, has some junk in it - not well structured html
            clean_text = li_element.text.strip('[').strip()
            if ' ' in clean_text:
                #print 'NO - ' + clean_text
                # skip any number that is not a single word
                pass
            else:
                self.results[number].append(clean_text)

        return self.results[number]

    def fractions(self):
        ''' Returns with fractions.
        Examples: 1/2, 1/3, ... 5/6, ... 9/10.
        '''
        result = {}
        for denominator in range(2, 11):
            for numerator in range(1, 10):
                if numerator < denominator:
                    number = str(numerator) + '/' + str(denominator)
                    result[number] = self.get_number(number)
        return result

    def small_fractions(self, min_power=2, max_power=3):
        ''' Returns with small fractions.
        Examples: 1/10, 2/10, ... 1/100, 2/100, ... 1/1000, ...
        '''
        result = {}
        for numerator in range(1, 11):
            for power in range(min_power, max_power):
                top = pow(10, power)
                for denominator in range(0, top, top / 10):
                    if numerator < denominator:
                        number = str(numerator) + '/' + str(denominator)
                        #print number
                        result[number] = self.get_number(number)
        return result

    def range(self, min_value, max_value):
        ''' Returns with a range of values. '''
        result = {}
        for number in range(min_value, max_value + 1):
            result[number] = self.get_number(str(number))
        return result

    def large_numbers(self, min_power=1, max_power=3):
        ''' Returns with large numbers power of 10s.
        Examples: 10, 20, 30, ... 100, 200, 300, ... 1000, 2000, 3000, ...
        '''
        result = {}
        for power in range(min_power, max_power):
            top = pow(10, power)
            for number in range(0, top, top / 10):
                if number == 0:
                    continue
                result[number] = self.get_number(str(number))

        return result

if __name__ == '__main__':
    API = HelyesirasAPI()
    # only for testing
    API.range(18, 22)

    # this is the real deal
    #API.fractions()
    #API.small_fractions(1, 4)
    #API.range(0, 2000)
    #API.large_numbers(1, 103)

    # save the results in different formats
    with open('numbers.hu.json', 'w+') as f_p:
        json.dump(API.results, f_p, indent=2)

    with open('numbers.txt', 'w+') as f_p:
        for number_value in API.results:
            for number_text in API.results[number_value]:
                f_p.write(number_value + ' ' + number_text.encode('UTF-8') + os.linesep)

    with open('numbers.hu.txt', 'w+') as f_p:
        for number_value in API.results:
            for number_text in API.results[number_value]:
                f_p.write(number_text.encode('UTF-8') + os.linesep)


    print API.results
    print 'Done'
