"The pymarc.field file."

from pymarc.constants import SUBFIELD_INDICATOR, END_OF_FIELD

class Field(object):
    """
    Field() pass in the field tag, indicators and subfields for the tag.

        field = Field(
            tag = '245',
            indicators = ['0','1'],
            subfields = [
                'a', 'The pragmatic programmer : ',
                'b', 'from journeyman to master /', 
                'c', 'Andrew Hunt, David Thomas.',
            ]

    If you want to create a control field, don't pass in the indicators
    and use a data parameter rather than a subfields parameter:

        field = Field(tag='001', data='fol05731351')

    """
    def __init__(self, tag, indicators=None, subfields=None, data=''):
        if indicators == None: 
            indicators = []
        if subfields == None:
            subfields = []

        self.tag = '%03s' % tag
        if self.tag < '010':
            self.data = data
        else: 
            self.indicators = indicators
            self.indicator1 = indicators[0] 
            self.indicator2 = indicators[1] 
            self.subfields = subfields 

    def __iter__(self):
        self.__pos = 0
        return self

    def __str__(self):
        """
        A Field object in a string context will return the tag, indicators
        and subfield as a string. This follows MARCMaker format; see [1]
        and [2] for further reference. Special character mnemonic strings
        have yet to be implemented (see [3]), so be forewarned. Note also
        for complete MARCMaker compatibility, you will need to change your
        newlines to DOS format ('\r\n').
        
        [1] http://www.loc.gov/marc/makrbrkr.html#mechanics
        [2] http://search.cpan.org/~eijabb/MARC-File-MARCMaker/
        [3] http://www.loc.gov/marc/mnemonics.html
        """
        if self.is_control_field(): 
            text = '=%s  %s' % (self.tag, self.data.replace(' ','\\'))
        else:
            text = '=%s  ' % (self.tag)
            for indicator in self.indicators:
                if indicator in (' ','\\'):
                    text += '\\'
                else:
                    text += '%s' % indicator
            for subfield in self:
                text += ('$%s%s' % subfield) 
        return text

    def __getitem__(self, subfield):
        """
        Retrieve the first subfield with a given subfield code in a field:

            field['a']

        Handy for quick lookups.
        """
        subfields = self.get_subfields(subfield)
        if len(subfields) > 0: 
            return subfields[0]
        return None

    def next(self):
        "Needed for iteration."
        while self.__pos < len(self.subfields):
            subfield = (self.subfields[ self.__pos ],
                self.subfields[ self.__pos+1 ])
            self.__pos += 2
            return subfield
        raise StopIteration

    def value(self):
        """
        Returns the field as a string without tag, indicators, and 
        subfield indicators.
        """
        if self.is_control_field():
            return self.data
        string = ""
        for subfield in self:
            string += subfield[1]
        return string

    def get_subfields(self, *codes):
        """
        get_subfields() accepts one or more subfield codes and returns
        a list of subfield values.  The order of the subfield values
        in the list will be the order that they appear in the field.

            print field.get_subfields('a')
            print field.get_subfields('a', 'b', 'z')
        """
        values = []
        for subfield in self:
            if subfield[0] in codes:
                values.append(subfield[1])
        return values 

    def add_subfield(self, code, value):
        """
        Adds a subfield code/value pair to the field.

            field.add_subfield('u', 'http://www.loc.gov')
        """
        self.subfields.append(code)
        self.subfields.append(value)

    def is_control_field(self):
        """
        returns true or false if the field is considered a control field.
        Control fields lack indicators and subfields.
        """
        if self.tag < '010': 
            return True
        return False

    def as_marc21(self):
        """
        used during conversion of a field to raw marc
        """
        if self.is_control_field():
            return self.data + END_OF_FIELD
        marc = str(self.indicator1) + str(self.indicator2)
        for subfield in self:
            marc += SUBFIELD_INDICATOR + subfield[0] + subfield[1]
        return marc + END_OF_FIELD

    def format_field(self):
        """
        Returns the field as a string without tag, indicators, and
        subfield indicators. Like pymarc.Field.value(), but prettier
        (adds spaces, formats subject headings).
        """
        if self.is_control_field(): 
            return self.data
        fielddata = ''
        for subfield in self:
            if not self.is_subject_field():
                fielddata += ' %s' % subfield[1]
            else:
                if subfield[0] not in ('v', 'x', 'y', 'z'):
                    fielddata += ' %s' % subfield[1]
                else: fielddata += ' -- %s' % subfield[1]
        return fielddata.strip()
    
    def is_subject_field(self):
        """
        Returns True or False if the field is considered a subject
        field.  Used by format_field.
        """
        if self.tag.startswith('6'): 
            return True
        return False