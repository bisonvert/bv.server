// Cross-browser event handlers.
function addEvent(obj, evType, fn) {
    if (obj.addEventListener) {
        obj.addEventListener(evType, fn, false);
        return true;
    } else if (obj.attachEvent) {
        var r = obj.attachEvent("on" + evType, fn);
        return r;
    } else {
        return false;
    }
}

Panel = Class.create({
    initialize: function(element, panel, options) {
        element = $(element);
        this.element = element;
        this.panel = $(panel);
        this.active = false;

        if(this.setOptions)
            this.setOptions(options);
        else
            this.options = options || { };

        this.options.onShow       = this.options.onShow || 
            function(element, panel){ 
                if(!panel.style.position || panel.style.position=='absolute') {
                    panel.style.position = 'absolute';
                    Position.clone(element, panel, {
                        setHeight: false, 
                        offsetTop: element.offsetHeight
                    });
                }
                Effect.Appear(panel,{duration:0.15});
            };
        this.options.onHide = this.options.onHide || 
            function(element, panel){ new Effect.Fade(panel,{duration:0.15}) };
    },

    show: function() {
        if (Element.getStyle(this.panel, 'display')=='none') 
            this.options.onShow(this.element, this.panel);
        if (!this.iefix && 
        (Prototype.Browser.IE) &&
        (Element.getStyle(this.panel, 'position')=='absolute')) {
            new Insertion.After(this.panel, 
            '<iframe id="' + this.panel.id + '_iefix" '+
            'style="display:none;position:absolute;filter:progid:DXImageTransform.Microsoft.Alpha(opacity=0);" ' +
            'src="javascript:false;" frameborder="0" scrolling="no"></iframe>');
            this.iefix = $(this.panel.id+'_iefix');
        }
        if(this.iefix) 
            setTimeout(this.fixIEOverlapping.bind(this), 50);
        this.active = true;
        obj_this = this;
        addEvent(window, 'click', function() { obj_this.hide(); return true; });
    },

    fixIEOverlapping: function() {
        Position.clone(this.panel, this.iefix, {setTop:(!this.panel.style.height)});
        this.iefix.style.zIndex = 1;
        this.panel.style.zIndex = 2;
        Element.show(this.iefix);
    },

    hide: function() {
        if (Element.getStyle(this.panel, 'display')!='none') 
            this.options.onHide(this.element, this.panel);
        if (this.iefix) 
            Element.hide(this.iefix);
        this.active = false;
    },

    toggle: function() {
        if (this.active)
            this.hide();
        else
            this.show();
    }
});


autocomplete_url = "/ajax/get_city/";
autocomplete_paramName = "value";
autocomplete_frequency = 0.2;
autocomplete_minChars = 3;
