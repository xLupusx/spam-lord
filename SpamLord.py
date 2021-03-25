import sys
import os
import re
import pprint


def process_file(name, f):
    """
    TODO
    This function takes in a filename along with the file object (actually
    a StringIO object at submission time) and
    scans its contents against regex patterns. It returns a list of
    (filename, type, value) tuples where type is either an 'e' or a 'p'
    for e-mail or phone, and value is the formatted phone number or e-mail.
    The canonical formats are:
         (name, 'p', '###-###-#####')
         (name, 'e', 'someone@something')
    If the numbers you submit are formatted differently they will not
    match the gold answers

    NOTE: ***don't change this interface***, as it will be called directly by
    the submit script

    NOTE: You shouldn't need to worry about this, but just so you know, the
    'f' parameter below will be of type StringIO at submission time. So, make
    sure you check the StringIO interface if you do anything really tricky,
    though StringIO should support most everything.
    """
    # You should change most or all of this for the function to work.
    res = []
    email = []
    eSpecial = []
    phone = []
    pSpecial = []
    for line in f:
        # processing email
        line = re.sub(r'\s\(followed.+?\@','@', line)
        email += re.findall(r'[\w\d.-]+@[\w\d.-]+\.\w+', line)        
        eSpecial += re.findall(r'[\S]+-@-[\S]+-\.-[\S]+', line)
        eSpecial += re.findall(r'[\w\d.-]+(?:\s@\s|\sWHERE\s)[\w\d]+(?:\.|\sDOM\s)[\w\d.-]+',line)
        eSpecial += re.findall(r'[\w\d.-]+(?:\%20at\%20)[\w\d]+(?:\%20dot\%20)[\w\d.-]+', line)
        eSpecial += re.findall(r'[\w\d.-]+(?:\&\#x40\;|\sat\s|\[at\]|\(at\))[\w\d]+(?:\.|\sdot\s|\[dot\]|\(dot\)|\sdt\s|\;)*[\w\d.-]+(?:\.|\sdot\s|\[dot\]|\(dot\)|\sdt\s|\;)[\w\d.-]+', line)
        # processing phone number
        phone += re.findall(r'\d{3}-\d{3}-\d{4}', line)        
        pSpecial += re.findall(r'\(\d{3}\)\s*\d{3}-\d{4}', line)
        pSpecial += re.findall(r'\d{3}\s\d{3}\s\d{4}', line)
        pSpecial += re.findall(r'\d{3}\s\d{3}-\d{4}', line)
    fName = os.path.basename(f.name)
    for x in eSpecial:
        if x[len(x)-1] == '.':
            eSpecial.remove(x)
            break
        if re.search(r'[Ss]erver',x):
            eSpecial.remove(x)
            break
        x = re.sub(r'-','', x)
        x = re.sub(r'\&\#x40\;|\sat\s|\[at\]|\(at\)|\%20at\%20|\s@\s|\sWHERE\s','@', x)        
        x = re.sub(r'\sdot\s|\[dot\]|\(dot\)|\%20dot\%20|\sDOM\s|\sdt\s|\;','.', x)
        email.append(x)
    for x in pSpecial:
        x = re.sub(r'\s|-|\(|\)','',x)
        newX = x[:3]+'-'+x[3:6]+'-'+x[6:]
        phone.append(newX)
    for x in email:
        res.append((fName, 'e', x))
    for x in phone:
        res.append((fName, 'p', x))
    return res


def process_dir(data_path):
    """
    You should not need to edit this function, nor should you alter
    its interface as it will be called directly by the submit script
    """
    # get candidates
    guess_list = []
    for fname in os.listdir(data_path):
        if fname[0] == '.':
            continue
        path = os.path.join(data_path, fname)
        f = open(path, 'r', encoding='latin-1')
        f_guesses = process_file(fname, f)
        guess_list.extend(f_guesses)
    return guess_list


def get_gold(gold_path):
    """
    You should not need to edit this function.
    Given a path to a tsv file of gold e-mails and phone numbers
    this function returns a list of tuples of the canonical form:
    (filename, type, value)
    """
    # get gold answers
    gold_list = []
    f_gold = open(gold_path, 'r', encoding='utf8')
    for line in f_gold:
        gold_list.append(tuple(line.strip().split('\t')))
    return gold_list


def score(guess_list, gold_list):
    """
    You should not need to edit this function.
    Given a list of guessed contacts and gold contacts, this function
    computes the intersection and set differences, to compute the true
    positives, false positives and false negatives.  Importantly, it
    converts all of the values to lower case before comparing
    """
    guess_list = [
        (fname, _type, value.lower())
        for (fname, _type, value)
        in guess_list
    ]
    gold_list = [
        (fname, _type, value.lower())
        for (fname, _type, value)
        in gold_list
    ]
    guess_set = set(guess_list)
    gold_set = set(gold_list)

    tp = guess_set.intersection(gold_set)
    fp = guess_set - gold_set
    fn = gold_set - guess_set

    pp = pprint.PrettyPrinter()
    # print 'Guesses (%d): ' % len(guess_set)
    # pp.pprint(guess_set)
    # print 'Gold (%d): ' % len(gold_set)
    # pp.pprint(gold_set)
    print('True Positives (%d): ' % len(tp))
    pp.pprint(tp)
    print('False Positives (%d): ' % len(fp))
    pp.pprint(fp)
    print('False Negatives (%d): ' % len(fn))
    pp.pprint(fn)
    print('Summary: tp=%d, fp=%d, fn=%d' % (len(tp), len(fp), len(fn)))


def main(data_path, gold_path):
    """
    You should not need to edit this function.
    It takes in the string path to the data directory and the
    gold file
    """
    guess_list = process_dir(data_path)
    gold_list = get_gold(gold_path)
    score(guess_list, gold_list)

"""
commandline interface takes a directory name and gold file.
It then processes each file within that directory and extracts any
matching e-mails or phone numbers and compares them to the gold file
"""
if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print('usage:\tSpamLord.py <data_dir> <gold_file>')
        sys.exit(0)
    main(sys.argv[1], sys.argv[2])
