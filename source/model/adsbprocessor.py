#!/usr/bin/python


import socket               # Import socket module
import sys
import stuff    
from sets import Set
import time
import math

class ADSB_Extended_Squitter(object):

    def __init__(self, string):
        self.binstring = stuff.asciistring_to_binstring(string)
    
    @property
    def DF(self):
        return stuff.binstring_to_int(self.binstring[0:5])

    @property
    def CA(self):
        return stuff.binstring_to_int(self.binstring[5:8])

    @property
    def ICAO(self):
        return stuff.binstring_to_int(self.binstring[8:32])

    @property
    def ADSB_BINARY_DATA(self):
        return self.binstring[32:88]

    @property
    def PARITY(self):
        return stuff.binstring_to_int(self.binstring[88:112])

    @property
    def TC(self):
        return stuff.binstring_to_int(self.ADSB_BINARY_DATA[0:5])


    # TC = X (Airborne Position)

    @property
    def F(self):
        return stuff.binstring_to_int(self.ADSB_BINARY_DATA[21:22])

    @property
    def T(self):
        return stuff.binstring_to_int(self.ADSB_BINARY_DATA[20:21])

    @property
    def LATITUDE(self):
        return stuff.binstring_to_int(self.ADSB_BINARY_DATA[22:39])

    @property
    def LONGITUDE(self):
        return stuff.binstring_to_int(self.ADSB_BINARY_DATA[39:56])



class ADSB_Extractor(object):

    modes_checksum_table = (
        0x3935ea, 0x1c9af5, 0xf1b77e, 0x78dbbf, 0xc397db, 0x9e31e9, 0xb0e2f0, 0x587178,
        0x2c38bc, 0x161c5e, 0x0b0e2f, 0xfa7d13, 0x82c48d, 0xbe9842, 0x5f4c21, 0xd05c14,
        0x682e0a, 0x341705, 0xe5f186, 0x72f8c3, 0xc68665, 0x9cb936, 0x4e5c9b, 0xd8d449,
        0x939020, 0x49c810, 0x24e408, 0x127204, 0x093902, 0x049c81, 0xfdb444, 0x7eda22,
        0x3f6d11, 0xe04c8c, 0x702646, 0x381323, 0xe3f395, 0x8e03ce, 0x4701e7, 0xdc7af7,
        0x91c77f, 0xb719bb, 0xa476d9, 0xadc168, 0x56e0b4, 0x2b705a, 0x15b82d, 0xf52612,
        0x7a9309, 0xc2b380, 0x6159c0, 0x30ace0, 0x185670, 0x0c2b38, 0x06159c, 0x030ace,
        0x018567, 0xff38b7, 0x80665f, 0xbfc92b, 0xa01e91, 0xaff54c, 0x57faa6, 0x2bfd53,
        0xea04ad, 0x8af852, 0x457c29, 0xdd4410, 0x6ea208, 0x375104, 0x1ba882, 0x0dd441,
        0xf91024, 0x7c8812, 0x3e4409, 0xe0d800, 0x706c00, 0x383600, 0x1c1b00, 0x0e0d80,
        0x0706c0, 0x038360, 0x01c1b0, 0x00e0d8, 0x00706c, 0x003836, 0x001c1b, 0xfff409,
        0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
        0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
        0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000)

    charset = '#ABCDEFGHIJKLMNOPQRSTUVWXYZ#####_###############0123456789######'
    
    def __init__(self):
        self.recent_airborne_position_adsb_objs = []


    # The NL function uses the precomputed table from 1090-WP-9-14
    def cprNLFunction(self, lat):
        if (lat < 0): lat = -lat    # Table is symmetric about the equator.
        if (lat < 10.47047130): result = 59
        elif (lat < 14.82817437): result = 58
        elif (lat < 18.18626357): result = 57
        elif (lat < 21.02939493): result = 56
        elif (lat < 23.54504487): result = 55
        elif (lat < 25.82924707): result = 54
        elif (lat < 27.93898710): result = 53
        elif (lat < 29.91135686): result = 52
        elif (lat < 31.77209708): result = 51
        elif (lat < 33.53993436): result = 50
        elif (lat < 35.22899598): result = 49
        elif (lat < 36.85025108): result = 48
        elif (lat < 38.41241892): result = 47
        elif (lat < 39.92256684): result = 46
        elif (lat < 41.38651832): result = 45
        elif (lat < 42.80914012): result = 44
        elif (lat < 44.19454951): result = 43
        elif (lat < 45.54626723): result = 42
        elif (lat < 46.86733252): result = 41
        elif (lat < 48.16039128): result = 40
        elif (lat < 49.42776439): result = 39
        elif (lat < 50.67150166): result = 38
        elif (lat < 51.89342469): result = 37
        elif (lat < 53.09516153): result = 36
        elif (lat < 54.27817472): result = 35
        elif (lat < 55.44378444): result = 34
        elif (lat < 56.59318756): result = 33
        elif (lat < 57.72747354): result = 32
        elif (lat < 58.84763776): result = 31
        elif (lat < 59.95459277): result = 30
        elif (lat < 61.04917774): result = 29
        elif (lat < 62.13216659): result = 28
        elif (lat < 63.20427479): result = 27
        elif (lat < 64.26616523): result = 26
        elif (lat < 65.31845310): result = 25
        elif (lat < 66.36171008): result = 24
        elif (lat < 67.39646774): result = 23
        elif (lat < 68.42322022): result = 22
        elif (lat < 69.44242631): result = 21
        elif (lat < 70.45451075): result = 20
        elif (lat < 71.45986473): result = 19
        elif (lat < 72.45884545): result = 18
        elif (lat < 73.45177442): result = 17
        elif (lat < 74.43893416): result = 16
        elif (lat < 75.42056257): result = 15
        elif (lat < 76.39684391): result = 14
        elif (lat < 77.36789461): result = 13
        elif (lat < 78.33374083): result = 12
        elif (lat < 79.29428225): result = 11
        elif (lat < 80.24923213): result = 10
        elif (lat < 81.19801349): result = 9
        elif (lat < 82.13956981): result = 8
        elif (lat < 83.07199445): result = 7
        elif (lat < 83.99173563): result = 6
        elif (lat < 84.89166191): result = 5
        elif (lat < 85.75541621): result = 4
        elif (lat < 86.53536998): result = 3
        elif (lat < 87.00000000): result = 2
        else:   result = 1
        return result


    def cprNFunction(self, lat, isodd):
        nl = self.cprNLFunction(lat) - isodd
        if nl < 1:
            nl = 1
        return nl


    def calculate_checksum(self, message):
        crc = 0
        for i in range(112):
            byte = i/8
            bit = i%8
            bitmask = 1 << (7 - bit)
            if ( ord( message[byte] ) & bitmask ):
                crc ^= self.modes_checksum_table[i]
        return crc


    def extended_squitter_strings(self, string):
        messages = []
        for i in range(len(string) - 14):
            if (ord(string[i]) >> 3) == 17:
                crc = self.calculate_checksum(string[i:i+14])
                if crc == stuff.binstring_to_int(stuff.asciistring_to_binstring(string[i+11:i+14])):
                    messages.append(string[i:i+14])
        return messages


    def decode_CPR(self, old_adsb_obj, new_adsb_obj):
        
        if (old_adsb_obj.F == 0 and new_adsb_obj.F == 0) or (old_adsb_obj.F == 1 and new_adsb_obj.F == 1):
            return None

        if old_adsb_obj.F == 0:
            even_adsb_obj_is_newest = False
            even_adsb_obj = old_adsb_obj
            odd_adsb_obj = new_adsb_obj
        else:
            even_adsb_obj_is_newest = True
            even_adsb_obj = new_adsb_obj
            odd_adsb_obj = old_adsb_obj

        lat_cpr_even = 1.0 * even_adsb_obj.LATITUDE / 131072
        lon_cpr_even = 1.0 * even_adsb_obj.LONGITUDE / 131072
        lat_cpr_odd = 1.0 * odd_adsb_obj.LATITUDE / 131072
        lon_cpr_odd = 1.0 * odd_adsb_obj.LONGITUDE / 131072

        air_d_lat_even = 360.0 / 60
        air_d_lat_odd = 360.0 / 59

        j = math.floor(59 * lat_cpr_even - 60 * lat_cpr_odd + 0.5)

        lat_even = (air_d_lat_even * (j % 60 + lat_cpr_even))
        lat_odd = (air_d_lat_odd * (j % 59 + lat_cpr_odd))

        if lat_even >= 270:
            lat_even = lat_even - 360

        if lat_odd >= 270:
            lat_odd = lat_odd - 360

        # Check zone here - IMPORTANT
        if self.cprNLFunction(lat_even) != self.cprNLFunction(lat_odd):
            #print '....................................... ZOOOOOOOOOOONE'
            return None


        if even_adsb_obj_is_newest:
            ni = self.cprNFunction(lat_even, 0)
            m = math.floor(lon_cpr_even * (self.cprNLFunction(lat_even) - 1) - lon_cpr_odd * self.cprNLFunction(lat_even) + 0.5)
            lon = (360.0 / ni) * (m % ni + lon_cpr_even)
            lat = lat_even
        else:
            ni = self.cprNFunction(lat_odd, 1)
            m = math.floor(lon_cpr_even * (self.cprNLFunction(lat_odd) - 1) - lon_cpr_odd * self.cprNLFunction(lat_odd) + 0.5)
            lon = (360.0 / ni) * (m % ni + lon_cpr_odd)
            lat = lat_odd

        return (lat, lon)


    def extract_aircraft_identification(self, adsb_obj):

        csbin = adsb_obj.ADSB_BINARY_DATA[8:]
        
        cs = ''
        cs += self.charset[ stuff.binstring_to_int(csbin[0:6]) ]
        cs += self.charset[ stuff.binstring_to_int(csbin[6:12]) ]
        cs += self.charset[ stuff.binstring_to_int(csbin[12:18]) ]
        cs += self.charset[ stuff.binstring_to_int(csbin[18:24]) ]
        cs += self.charset[ stuff.binstring_to_int(csbin[24:30]) ]
        cs += self.charset[ stuff.binstring_to_int(csbin[30:36]) ]
        cs += self.charset[ stuff.binstring_to_int(csbin[36:42]) ]
        cs += self.charset[ stuff.binstring_to_int(csbin[42:48]) ]

        chars_to_remove = ['_', '#']
        callsign = cs.translate(None, ''.join(chars_to_remove))

#        print 'ICAO: ' + str(adsb_obj.ICAO) + '   Callsign: ' + callsign

        return (adsb_obj.ICAO, callsign)


    def extract_altitude(self, adsb_obj):

        alt_string = adsb_obj.ADSB_BINARY_DATA[8:20]
        Q = alt_string[7]

        new_alt_string = alt_string[0:7] + alt_string[8:]

        if Q == '0':
            altitude = stuff.binstring_to_int(new_alt_string) * 100 - 1000
        else:
            altitude = stuff.binstring_to_int(new_alt_string) * 25 - 1000

        return altitude



    def extract_airborne_position(self, adsb_obj):

        # Here we make sure that all stored objects are not older than 10 seconds.
        present_time = time.time()

        all_recent_adsb_objs_fresh = False

        while not all_recent_adsb_objs_fresh:
            if len(self.recent_airborne_position_adsb_objs) > 0:

                oldest_time, oldest_adsb_obj = self.recent_airborne_position_adsb_objs[0]
                if (present_time - oldest_time) > 10.0:
                    self.recent_airborne_position_adsb_objs.pop(0)

#                    print '\nICAO: ' + str(oldest_adsb_obj.ICAO) + '.................... Package removed due to being older than 10s\n'

                else:
                    all_recent_adsb_objs_fresh = True

            else:
                break


        # If there exists a recent saved message with the same ICAO number, proceed...
        if adsb_obj.ICAO in Set( [stored_adsb_obj.ICAO for (stored_time, stored_adsb_obj) in self.recent_airborne_position_adsb_objs] ):

            # A previous message with same ICAO number exists, get its position in list
            pos = [obj.ICAO for (_, obj) in self.recent_airborne_position_adsb_objs].index(adsb_obj.ICAO)

            _, old_adsb_obj = self.recent_airborne_position_adsb_objs.pop(pos)
            new_adsb_obj = adsb_obj
            
            # Append the new message to list
            self.recent_airborne_position_adsb_objs.append( (present_time, new_adsb_obj) )

            # Process the two packages
            result = self.decode_CPR(old_adsb_obj, new_adsb_obj)

            if result:
                latitude, longitude = result    
                altitude = self.extract_altitude(new_adsb_obj)

                # Extract altitude here instead of in the method above!!!!

#                print 'ICAO: ' + str(new_adsb_obj.ICAO) + '   Altitude: ' + str(altitude) + '   Latitude: ' + str(latitude) + '   Longitude: ' + str(longitude)
                return (new_adsb_obj.ICAO, altitude, longitude, latitude)
            else:
                
                return None

        else:
            
            # Append message to list
            self.recent_airborne_position_adsb_objs.append( (present_time, adsb_obj) )

            return None


    def extract_airborne_velocity(self, adsb_obj):
        
        return None



    def extract(self, received_string):
        
        extracted_info = {'callsigns': [], 'positions': [], 'velocities': []}
        
        something_added = False

        for each in self.extended_squitter_strings(received_string):

            adsb_obj = ADSB_Extended_Squitter(each)
            
            if adsb_obj.TC >= 1 and adsb_obj.TC <= 4:

                result = self.extract_aircraft_identification(adsb_obj)
                if result:
                    extracted_info['callsigns'].append( result )
                    something_added = True

            elif adsb_obj.TC >= 9 and adsb_obj.TC <= 18:

                result = self.extract_airborne_position(adsb_obj)
                if result:
                    extracted_info['positions'].append( result )
                    something_added = True

            elif adsb_obj.TC == 19:

                result = self.extract_airborne_velocity(adsb_obj)

                if result:
                    extracted_info['velocities'].append( result )
                    something_added = True

            else:
                pass
                

        if something_added:
            return extracted_info
        else:
            return None



if __name__ == '__main__':

    p = ADSB_Extractor()

    s = socket.socket()         # Create a socket object
    host = socket.gethostbyname('sl6bh.dyndns.org')

    port = 30334                

    s.connect((host, port))

    print 'Processing data from ' + host + ', port ' + str(port)

    largest_chunk_size = 0

    try:
        while True:
            chunk = s.recv(1024*12)     # ??????????
         
            t0 = time.time()

            extracted_information = p.extract(chunk)
            
            if extracted_information:

                print extracted_information

#            print str(len(chunk)) + ' bytes processed in ' + str(time.time() - t0) + 's.'
            
            if len(chunk) > largest_chunk_size:
                largest_chunk_size = len(chunk)

            #print 'DONE PROCESSING ' + str(len(chunk)) + ' BYTES\n'

        # Hmmm.... Lets que the chunks in another thread for execution. 

    except KeyboardInterrupt:
        s.close                     # Close the socket when done
        print 'Exited gracefully!'
        print 'Largest observed chunk was ' + str(largest_chunk_size) + ' bytes.'
        sys.exit(0)
