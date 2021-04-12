import numpy.random as npr
from termcolor import colored
import json
import argparse
import time
import os

def alphagram(word):
  return ''.join(sorted(list(word)))

def create_sm_data(word_data):
  sm_data = []
  sorted_alphagrams = [(key, int(word_data[key][0]['probability_order'])) for key in word_data.keys()]
  sorted_alphagrams.sort(key=lambda x: x[1])
  for (alphagram, _) in sorted_alphagrams:
    sm_data.append({
      'alphagram': alphagram,
      'n': 0,
      'e': 2.5,
      'i': 1,
      'last-reviewed': float('inf')
      })
  save_sm_data(sm_data)

def test_word(alphagram, word_entry):
  all_bingos = [word['word'] for word in word_entry]
  missing_bingos = all_bingos[:]
  found_bingos = []
  total_bingos = len(word_entry)

  hint_length = 1
  num_incorrect = 0
  num_hints = 0
  while len(found_bingos) < total_bingos:
    answer = input(alphagram + '[' + str(len(found_bingos)) + '/' + str(total_bingos) + ']: ')
    answer = str.upper(answer).strip()
    if answer in missing_bingos:
      # print(colored("good",'green'))
      found_bingos.append(answer)
      missing_bingos.remove(answer)
      answer_idx = all_bingos.index(answer)
      print(colored(word_entry[answer_idx]['front_hooks'], 'green'),
        ".",
        colored(word_entry[answer_idx]['word'], 'green'),
        ".",
        colored(word_entry[answer_idx]['back_hooks'], 'green'),
        "–",
        word_entry[answer_idx]['definition'])
      hint_length = 1
    elif answer in found_bingos:
      print(colored("repeat", "yellow"))
    elif answer == "":
      print(missing_bingos[0][:hint_length])
      hint_length += 1
      num_hints += 1
    elif answer == "Q":
      exit()
    else:
      print(colored("phony",'red'))
      num_incorrect += 1
  print('')
  return num_hints, num_incorrect

def sm_test_word(sm_entry, word_entry):
  num_hints, num_incorrect = test_word(sm_entry['alphagram'], word_entry)
  grade = performance(num_hints, num_incorrect)
  n, e, i = sm_2(grade, sm_entry['n'], sm_entry['e'], sm_entry['i'])
  sm_entry['n'], sm_entry['e'], sm_entry['i'] = n, e, i
  sm_entry['last-reviewed'] = int(time.time())

  # hack to make flashcarding possible at a similar time every day
  sm_entry['i'] -= 1.0 / 24

  return grade

def performance(num_hints, num_incorrect):
  return int(max(0, 5 - 1.5 * num_hints - 2 * num_incorrect))

def sm_2(q, n, e, i):
  if q >= 4:
    if n == 0:
      i = 1
    elif n == 1:
      i = 6
    else:
      i = i * e

    e = e + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    if e < 1.3:
      e = 1.3
    n += 1
  else:
    n = 0
    i = 1

  return (n, e, i)

def save_sm_data(sm_data):
  with open(flashcard_directory + 'sm_data.txt', 'w') as outfile:
    json.dump(sm_data, outfile)

def print_stats(sm_data):
  # by probability
  num_entries = [0] * 5
  for i, sm_entry in enumerate(sm_data):
    if sm_entry['last-reviewed'] < float('inf'):
      if i < 250:
        num_entries[0] += 1
      elif i < 500:
        num_entries[1] += 1
      elif i < 1000:
        num_entries [2] += 1
      elif i < 2000:
        num_entries[3] += 1
      else:
        num_entries[4] += 1
  print(colored('Cards in deck by probability:',attrs=['bold']))
  print('<250:\t', sum(num_entries[:1]))
  print('<500:\t',sum(num_entries[:2]))
  print('<1000:\t', sum(num_entries[:3]))
  print('<2000:\t', sum(num_entries[:4]))
  print('Total:\t', sum(num_entries[:5]))
  print('')

  # by interval
  num_entries = [0] * 5
  for sm_entry in sm_data:
    if sm_entry['last-reviewed'] < float('inf'):
      if sm_entry['i'] >= 30:
        num_entries[0] += 1
      elif sm_entry['i'] >= 20:
        num_entries[1] += 1
      elif sm_entry['i'] >= 10:
        num_entries [2] += 1
      elif sm_entry['i'] >= 5:
        num_entries[3] += 1
      else:
        num_entries[4] += 1
  print(colored('Cards in deck by inter-repetition interval:',attrs=['bold']))
  print('0-5:\t', num_entries[4])
  print('5-10:\t', num_entries[3])
  print('10-20:\t', num_entries[2])
  print('20-30:\t',num_entries[1])
  print('30+:\t', num_entries[0])
  print('')
  

def print_detailed_schedule(sm_data):
  # now, next hour, next day, next week, +
  num_entries = [0] * 5
  now_time = int(time.time())
  earliest_time = float('inf')
  for entry in sm_data:
    if entry['last-reviewed'] == - float('inf'):
      num_entries[0] += 1
      earliest_time = 0
    elif entry['last-reviewed'] <= now_time and entry['n'] == 0:
      num_entries[0] += 1
      earliest_time = 0
    elif entry['last-reviewed'] < float('inf'):
      next_review = ((entry['last-reviewed'] + 86400 * entry['i']) - now_time) / 3600
      earliest_time = min(earliest_time, int((entry['last-reviewed'] + 86400 * entry['i'] - now_time) / 60))
      if next_review <= 0:
        num_entries[0] += 1
      elif next_review <= 24:
        num_entries[1] += 1
      elif next_review <= 24 * 2:
        num_entries[2] += 1
      elif next_review <= 24 * 7:
        num_entries[3] += 1
      elif next_review <= 24 * 30:
        num_entries[4] += 1
  print(colored('Upcoming schedule:',attrs=['bold']))
  print('Next review:\t', max(earliest_time, 0), 'minutes')
  print('Now:\t\t', sum(num_entries[:1]))
  print('Today:\t\t', sum(num_entries[:2]))
  print('Two days:\t', sum(num_entries[:3]))
  print('Week:\t\t', sum(num_entries[:4]))
  print('Month:\t\t', sum(num_entries[:5]))
  print('')

def add_entries_to_deck(sm_data, number):
  newly_added = 0
  for sm_entry in sm_data:
    if sm_entry['last-reviewed'] == float('inf'):
      sm_entry['last-reviewed'] = - float('inf')
      newly_added += 1
      if newly_added >= number:
        break
  save_sm_data(sm_data)

def advance_time(sm_data, h):
  for sm_entry in sm_data:
    sm_entry['last-reviewed'] -= h * 3600
  save_sm_data(sm_data)


if __name__ == '__main__':

  parser = argparse.ArgumentParser(description="a command-line Scrabble study tool")
  parser.add_argument('--verbose', '-v', dest='v', action='store_const', const=True, default=False, help='verbose')
  parser.add_argument('--new', '-n', dest='n', action='store_const', const=True, default=False, help='new session: adds 20 words to deck')
  parser.add_argument('--add', '-a', dest='a', action='store_const', const=True, default=False, help='add entry mode')
  parser.add_argument('--schedule', dest='schedule', action='store_const', const=True, default=False, help='print upcoming schedule')
  parser.add_argument('--stats', dest='stats', action='store_const', const=True, default=False, help='print all-time stats')
  args = parser.parse_args()

  verboseprint = print if args.v else lambda *a, **k: None

  flashcard_directory = os.path.dirname(os.path.realpath(__file__)) + '/'

  with open(flashcard_directory + 'word_data.txt') as infile:
    word_data = json.load(infile)

  if not os.path.exists(flashcard_directory + 'sm_data.txt'):
    create_sm_data(word_data)
  with open(flashcard_directory + 'sm_data.txt') as infile:
    sm_data = json.load(infile)

  if args.n:
    add_entries_to_deck(sm_data, 20)

  # add mode

  if args.a:
    while True:
      to_add = input('add to deck: ')
      to_add = alphagram(str.upper(to_add).strip())
      if to_add == 'Q':
        exit()
      to_add_entry = None
      for sm_entry in sm_data:
        if sm_entry['alphagram'] == to_add:
          to_add_entry = sm_entry
          break
      if to_add_entry is not None:
        if to_add_entry['last-reviewed'] == float('inf'):
          to_add_entry['last-reviewed'] = - float('inf')
          save_sm_data(sm_data)
          print(to_add, 'added to deck')
        else:
          print(to_add, 'already in deck')
      else:
          print(to_add, 'is not a valid alphagram')

  # stats
  if args.stats:
    print_stats(sm_data)

  if args.schedule:
    print_detailed_schedule(sm_data)

  # flashcarding
  # missed entries
  missed_entries = list(npr.permutation([sm_entry for sm_entry in sm_data if
    sm_entry['last-reviewed'] <= int(time.time()) and sm_entry['n'] == 0]))
  if missed_entries:
    print('You have', len(missed_entries), 'missed alphagrams to review')
    while missed_entries:
      sm_entry = missed_entries.pop(0)
      grade = sm_test_word(sm_entry, word_data[sm_entry['alphagram']])
      save_sm_data(sm_data)
      if grade <= 3:
        missed_entries.append(sm_entry)
        
  # scheduled entries
  scheduled_entries = [sm_entry for sm_entry in sm_data if
    sm_entry['last-reviewed'] + 86400 * sm_entry['i'] <= int(time.time())]
  if scheduled_entries:
    print('You have', len(scheduled_entries), 'scheduled alphagrams to review')
    for sm_entry in npr.permutation(scheduled_entries):
      sm_test_word(sm_entry, word_data[sm_entry['alphagram']])
      save_sm_data(sm_data)

  # missed entries
  missed_entries = list(npr.permutation([sm_entry for sm_entry in sm_data if
    sm_entry['last-reviewed'] <= int(time.time()) and sm_entry['n'] == 0]))
  if missed_entries:
    print('You have', len(missed_entries), 'missed alphagrams to review')
    while missed_entries:
      sm_entry = missed_entries.pop(0)
      grade = sm_test_word(sm_entry, word_data[sm_entry['alphagram']])
      save_sm_data(sm_data)
      if grade <= 3:
        missed_entries.append(sm_entry)





