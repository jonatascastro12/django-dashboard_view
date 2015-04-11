function DashboardFilters(){

}

$('.filters input').keydown(function(e){
    if (e.keyCode == 13){
        $(this).change();
        $('#filter_button').click();
    }
});

$('#filter_button').click(function(){
    datatableview.initialized_datatables[0].api().ajax.reload();
});

$('#filter_clear_button').click(function(){
    for(var i=0; i<DashboardFilters.filters.length; i++){
        DashboardFilters.filters[i].clear();
    }
    datatableview.initialized_datatables[0].api().ajax.reload();
});

DashboardFilters.filters = [];

DashboardFilters.add_filter = function(obj){
    var result = $.grep(DashboardFilters.filters , function(e){ return e.field == obj.field && e.filter == obj.filter ; });
    if (result.length === 0){
        DashboardFilters.filters.push(obj);
    }else if (result.length === 1){
        result[0].data = obj.data
    }
};

DashboardFilters.add_datatable_filters = function(aoData){
    $.each(DashboardFilters.filters, function(i, e){
        aoData.push({name: 'filter-' + i + '-' + e.field+'-'+ e.filter , value: JSON.stringify(e.data)})
    });
};