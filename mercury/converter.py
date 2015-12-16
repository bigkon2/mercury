from re import sub


class Converter(object):
    kg_koef = 2.20462
    cwt_koef = 100
    meter_to_foot = 35.3146667

    def camel_case_to_underscore(self, name):
        s1 = sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def convert_weight(self, value, src_units, dest_units='lb'):
        v = float(value)
        s = src_units.lower()
        d = dest_units.lower()
        if s == d:
            return v
        if s == 'kg':
            v *= self.kg_koef
        elif s == 'cwt':
            v *= self.cwt_koef

        if d == 'kg':
            v /= self.kg_koef
        elif d == 'cwt':
            v /= self.cwt_koef
        return v

    def convert_volume(self, value, src_units, dest_units='cft'):
        v = float(value)
        s = src_units.lower()
        d = dest_units.lower()
        if s == d:
            return v
        if s in ('cbm', 'mt'):
            v *= self.meter_to_foot
        elif s == 'kg_acw':
            v *= self.kg_koef / 10.4

        if d in ('cbm', 'mt'):
            v /= self.meter_to_foot
        elif d == 'kg_acw':
            v *= 10.4 / self.kg_koef
        return v

    def get_shipment_type(self, tariff_type):
        t = tariff_type.lower()
        options = {
            'fcl_c': 'fclCased',
            'fcl_l': 'fclLoose',
            'air': 'air',
            'lcl': 'lcl',
            'road': 'road'
        }
        return options[t]

    def get_display_shipment_type(self, shipment_type):
        s = shipment_type.lower()
        options = {
            'fcl_c': 'FCL (Cased)',
            'fcl_l': 'FCL (Loose)',
            'air': 'Air',
            'lcl': 'LCL',
            'road': 'Road'
        }
        return options[s]

    def get_shipment_type_value(self, value):
        options = {
            'fclCased': 'FCL_C',
            'FCL (Cased)': 'FCL_C',
            'fclLoose': 'FCL_L',
            'FCL (Loose)': 'FCL_L',
            'air': 'Air',
            'AIR': 'Air',
            'lcl': 'LCL',
            'LCL': 'LCL',
            'road': 'Road',
            'Road': 'Road',
        }
        default = 'FCL_L'
        return options.get(value, default)

    def get_params_from_query(self, query_params):
        res = {self.camel_case_to_underscore(k): v
               for k, v in query_params.iteritems()}
        res['origin_ports'] = query_params.getlist('originPorts')
        res['destination_ports'] = query_params.getlist('destinationPorts')
        return res
