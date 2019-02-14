odoo.define('pos_ticket.models_extend', function (require){
    "use strict";
    var models = require('point_of_sale.models');
    var _super_order = models.Order.prototype;
     
    

    models.load_models([
        
        // Modulo de sequencia

        {
            model: 'ir.sequence', 
            fields: ['id','prefix','name','number_next_actual',
            'padding','code','number_next_actual','vitt_number_next_actual',
            'vitt_min_value','vitt_max_value','fiscal_sequence_regime_ids','sequence_id','expiration_date','active'],
            domain: [['code','=','pos.order'],['active','=',true]], 
            loaded: function(self,sequences)
            { self.sequences = sequences[0];
            },

        },

        // Modulo del SAR

        {
            model: 'vitt_fiscal_seq.fiscal_sequence_regime', 
            fields: ['authorization_code_id','id','actived'],
            // domain: [['id','=',this.get_id_sequence()]],
            domain: function(self){ return [['id','=', self.sequences.fiscal_sequence_regime_ids], [ 'actived','=', true ]]; },
            loaded: function(self, fiscal_codes)
            {
            self.fiscal_code = fiscal_codes[0];
            },
        }
    ]);


    models.Order = models.Order.extend
    ({
        // export_for_printing: function() 
        // {
        //     var json = _super_order.export_for_printing.apply(this,arguments);
        //     json.subtotal_in_words = this.get_subtotal_in_words();
        //     json.get_min_value = this.get_min_value();
        //     json.get_max_value = this.get_max_value();
        //     // json.get_cai = this.get_cai();
        //     return json;

        // },


        // Agregando los parametros del SAR 
        get_expiration_date : function (sequences) {
            // body...
            self = this;
            var expiration_date =  self.pos.sequences.expiration_date;
            return expiration_date;
        },

        get_id_sequence : function (sequences) {
            // body...
            self = this;
            var id_sequence =  self.pos.sequences.fiscal_sequence_regime_ids;
            return id_sequence;
        },

        get_min_value: function(sequences) {
            // body...
            self = this;
            var min_value =  self.pos.sequences.vitt_min_value;
            return min_value;
        },

        get_max_value: function(sequences) {
            // body...
            self = this;
            var max_value =  self.pos.sequences.vitt_max_value;
            return max_value;
        },

        get_cai: function(fiscal_code) {
            // body...
            self = this;
            var cai =  self.pos.fiscal_code.authorization_code_id[1];
            return cai;
        },

        get_subtotal_in_words: function(sequences){
            self = this;
            var prefix = self.pos.sequences.prefix;

            function sequense(num)
                {
                    
                    var s = ""+ num;
                    while (s.length < 8)
                    {
                        s = "0" + s;
                    }
                    return s;
                }

            var num =  self.pos.sequences.vitt_number_next_actual++;

            return prefix + sequense(num);
            // this.pos.click_next();
            // this.pos.set_next_number.destroy();




        }
    });
});


