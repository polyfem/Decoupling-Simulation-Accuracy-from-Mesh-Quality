for i = 1:2:
    postfix = 'good';
    if i == 2
        postfix = 'bad';
    end

    folder = ['cond_num' postfix];

    files = dir([folder '/mat_*']);

    n_refs = length(files) / 2;
    prefs = zeros(n_refs,1);
    nprefs = zeros(n_refs,1);

    for k = 1:length(files)
        mat_pat = files(k).name;

        pref = mat_pat(end-5) == 'f';

        if pref
            nref = str2double(mat_pat(end-10));
        else
            nref = str2double(mat_pat(end-5));
        end
        tic
        tmp = load([folder '/' mat_pat]);

        mat = sparse(tmp(2:end,1), tmp(2:end,2), tmp(2:end,3));
        assert(tmp(1,1) == tmp(1,2));
        assert(tmp(1,1) == length(mat));
        assert(nnz(mat) <= tmp(1,3));
        toc

        tic
        kk = condest(mat, 4);
        toc

        if pref
            prefs(nref+1) = kk;
        else
            nprefs(nref+1) = kk;
        end

        display(mat_pat)
        display([ num2str(k) '/' num2str(length(files))])
    end


    % figure;
    % semilogy(prefs, '*-')
    % hold on
    % semilogy(nprefs, '*-')
    % legend('Pref','P1');

    csvwrite(['conditioning_' postfix '_prefs.csv'], prefs);
    csvwrite(['conditioning_' postfix '_nprefs.csv'], nprefs);
end