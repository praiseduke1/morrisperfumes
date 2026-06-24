(function () {
    'use strict';

    var prov = document.querySelector('#id_province');
    var city = document.querySelector('#id_city');
    var dist = document.querySelector('#id_district');
    var pc = document.querySelector('#id_postal_code');

    if (!prov || !city) return;

    var TS_OPTIONS = {
        maxOptions: null,
        placeholder: 'Cari\u2026',
        searchField: ['text'],
        sortField: [{ field: 'text', direction: 'asc' }],
        render: {
            no_results: function () { return '<div class="p-2 text-stone-400 text-sm">Tidak ditemukan</div>'; },
        },
    };

    function initTomSelect(sel) {
        if (!sel || sel.tomselect || sel.disabled) return;
        new TomSelect(sel, TS_OPTIONS);
    }

    function destroyTomSelect(sel) {
        if (sel && sel.tomselect) {
            sel.tomselect.destroy();
        }
    }

    function syncTomSelect(sel) {
        destroyTomSelect(sel);
        if (sel && !sel.disabled && sel.options.length > 1) {
            new TomSelect(sel, TS_OPTIONS);
        }
    }

    function fetchJson(url, param, value) {
        return fetch(url + '?' + param + '=' + encodeURIComponent(value))
            .then(function (r) {
                if (!r.ok) throw new Error('Gagal memuat data (' + r.status + ')');
                return r.json();
            });
    }

    function populateSelect(select, data) {
        if (!select) return;
        select.innerHTML = '<option value="">Pilih\u2026</option>';
        data.forEach(function (item) {
            var opt = document.createElement('option');
            opt.value = item.id;
            opt.textContent = item.name || item.code;
            select.appendChild(opt);
        });
    }

    function resetSelect(select) {
        if (!select) return;
        select.innerHTML = '<option value="">Pilih\u2026</option>';
        select.disabled = true;
        destroyTomSelect(select);
    }

    function showError(message) {
        var container = prov.closest('form');
        if (!container) return;
        var banner = document.createElement('div');
        banner.className = 'cascade-error p-3 bg-rose-50 border border-rose-200 rounded-xl text-sm text-rose-600 mb-4';
        banner.textContent = message;
        container.prepend(banner);
        setTimeout(function () { if (banner.parentNode) banner.remove(); }, 5000);
    }

    function loadChild(parent, child, resetTargets) {
        var parentId = parent.value;

        resetTargets.forEach(function (s) { resetSelect(s); });

        if (!parentId) {
            child.innerHTML = '<option value="">Pilih\u2026</option>';
            child.disabled = true;
            destroyTomSelect(child);
            return;
        }

        if (child.tomselect) child.tomselect.showLoading();
        child.innerHTML = '<option value="">Memuat\u2026</option>';
        child.disabled = true;
        destroyTomSelect(child);

        var param = parent.name + '_id';
        var url = parent.dataset.url;
        if (!url) return;

        fetchJson(url, param, parentId).then(function (data) {
            populateSelect(child, data);
            child.disabled = false;
            syncTomSelect(child);
        }).catch(function (err) {
            child.innerHTML = '<option value="">Gagal memuat</option>';
            child.disabled = false;
            showError(err.message || 'Terjadi kesalahan saat memuat data wilayah.');
        });
    }

    initTomSelect(prov);

    prov.addEventListener('change', function () { loadChild(prov, city, [dist, pc]); });
    if (city) city.addEventListener('change', function () { loadChild(city, dist, [pc]); });
    if (dist) dist.addEventListener('change', function () { loadChild(dist, pc, []); });

    window.selectAddress = async function (id) {
        var card = document.querySelector('.address-card[data-id="' + id + '"]');
        if (!card || !prov || !city) return;

        document.querySelectorAll('.address-card').forEach(function (c) {
            c.classList.remove('border-amber-500', 'bg-amber-50/50');
            c.classList.add('border-stone-200', 'hover:border-stone-300', 'bg-white');
        });
        card.classList.remove('border-stone-200', 'hover:border-stone-300', 'bg-white');
        card.classList.add('border-amber-500', 'bg-amber-50/50');

        function setInput(name, val) {
            var el = document.querySelector('#id_' + name);
            if (el) el.value = val || '';
        }
        setInput('recipient_name', card.dataset.recipient);
        setInput('phone', card.dataset.phone);
        setInput('shipping_address', card.dataset.address);

        prov.value = card.dataset.provinceId || '';
        syncTomSelect(prov);

        try {
            if (prov.value && prov.dataset.url) {
                var cities = await fetchJson(prov.dataset.url, 'province_id', prov.value);
                populateSelect(city, cities);
                city.disabled = false;
                city.value = card.dataset.cityId || '';
                syncTomSelect(city);
            } else {
                resetSelect(city); resetSelect(dist); resetSelect(pc);
                return;
            }

            if (city.value && city.dataset.url) {
                var districts = await fetchJson(city.dataset.url, 'city_id', city.value);
                populateSelect(dist, districts);
                dist.disabled = false;
                dist.value = card.dataset.districtId || '';
                syncTomSelect(dist);
            } else {
                resetSelect(dist); resetSelect(pc);
                return;
            }

            if (dist.value && dist.dataset.url) {
                var codes = await fetchJson(dist.dataset.url, 'district_id', dist.value);
                populateSelect(pc, codes);
                pc.disabled = false;
                pc.value = card.dataset.postalcodeId || '';
                syncTomSelect(pc);
            } else {
                resetSelect(pc);
            }
        } catch (e) {
            showError('Gagal memuat data alamat. Silakan coba lagi.');
        }
    };
})();
