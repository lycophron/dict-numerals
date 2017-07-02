#!/usr/local/bin/python
import time
import os
import urllib2
from pyquery import PyQuery # easy_install PyQuery
import json

class HelyesirasAPI():
    api_requests = 0

    results = {}

    def get_number(self, number):
        if number in self.results:
            return self.results[number]
        else:
            self.results[number] = []

        # could not find any documentation about their API
        # let's use html, parse, then extract required information
        response = urllib2.urlopen('http://helyesiras.mta.hu/helyesiras/default/numerals?q=' + number)
        self.api_requests = self.api_requests + 1

        if self.api_requests % 5 == 0:
            print self.api_requests
        if self.api_requests % 100 == 0:
            # be mindful of API overloads
            time.sleep(1)

        html = response.read()
        #print html
        pq = PyQuery(html)
        #<ul class="result"><li>
        #print pq
        tag = pq('ul.result > li')
        for t in tag:
            # clean up the li tag, has some junk in it - not well structured html
            clean_text = t.text.strip('[').strip()
            if ' ' in clean_text:
                #print 'NO - ' + clean_text
                # skip any number that is not a single word
                pass
            else:
                self.results[number].append(clean_text)

        return self.results[number]

    def fractions(self):
        # examples 1/2, 1/3, ... 5/6, ... 9/10.
        result = {}
        for denominator in range(2, 11):
            for numerator in range(1, 10):
                if numerator < denominator:
                    number = str(numerator) + '/' + str(denominator)
                    result[number] = self.get_number(number)
        return result

    def small_fractions(self, min_power=2, max_power=3):
        # examples 1/10, 2/10, ... 1/100, 2/100, ... 1/1000, ...
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

    def range(self, min, max):
        result = {}
        for number in range(min, max + 1):
            result[number] = self.get_number(str(number))
        return result

    def large_numbers(self, min_power = 1, max_power = 3):
        # examples 10, 20, 30, ... 100, 200, 300, ... 1000, 2000, 3000, ...
        result = {}
        for power in range(min_power, max_power):
            top = pow(10, power)
            for number in range(0, top, top / 10):
                if number == 0:
                    continue
                result[number] = self.get_number(str(number))

        return result

if __name__ == '__main__':
    api = HelyesirasAPI()
    # only for testing
    api.range(18, 22)

    # this is the real deal
    #api.fractions()
    #api.small_fractions(1, 4)
    #api.range(0, 2000)
    #api.large_numbers(1, 103)

    # save the results in different formats
    with open('numbers.hu.json', 'w+') as f_p:
        json.dump(api.results, f_p, indent=2)

    with open('numbers.txt', 'w+') as f_p:
        for number in api.results:
            for number_text in api.results[number]:
                f_p.write(number + ' ' + number_text.encode('UTF-8') + os.linesep)

    with open('numbers.hu.txt', 'w+') as f_p:
        for number in api.results:
            for number_text in api.results[number]:
                f_p.write(number_text.encode('UTF-8') + os.linesep)


    print api.results
    print 'done'
