function calculate_performance(block)
%Calculate the performance of a subject on a session at the two-alternative
%forced-choice task (2AFC)and the two-alternative unforced choice (2AUC)
%International Brain Laboratory (IBL) set-up. For more details see Burgess
%et al., 2017 (Cell Reports) doi: 10.1016/j.celrep.2017.08.047.

%Part of IBL data analysis pipeline - Packer Lab

%2019-06 DAC created
duration = block.duration;
data = block.events;
countcorrect = 0;
countincorrect = 0;
countcorrectR = 0;
countincorrectR = 0;
countcorrectL = 0;
countincorrectL = 0;
countcorrectNOGO = 0;
countincorrectNOGO = 0;
countmissed = 0;
iii = 1;

contrastAbsValues = abs(data.contrastValues);
params = block.paramsValues;
numTrials = data.trialNumValues(end)- 1;

%response time. Assume open-loop and quiescent period have the same value
%in all trials
deltaTime = params(1).interactiveDelay;

%Substract one trial when in training mode - due to finishing the trial
%manually one non-finished trial is added
for ii = 1:numTrials
    %include only easy trials (>=40% contrast)
    if (contrastAbsValues(ii) == 1 || contrastAbsValues(ii) == 0.5 ||...
            contrastAbsValues(ii) == 0.4) ||...
            (data.contrastRightValues(ii) == 0 && data.contrastLeftValues(ii) == 0)
        %When forced repetition after a missed trial is ON, analyse only
        %the first of the repetitions
        if data.repeatNumValues(ii) == 1
            
            %Exclude trials that, in a closed-loop task, were missed
            if data.responseValues(ii) == 0 && data.feedbackValues(ii) == 0
                countmissed = countmissed + 1;
                %count the succesful ones and do it also for right, left
                %and NOGO choices
            elseif data.feedbackValues(ii) == 1
                countcorrect = countcorrect + 1 ;
                if data.contrastRightValues(ii) > 0
                    countcorrectR = countcorrectR + 1;
                elseif data.contrastLeftValues(ii) > 0
                    countcorrectL = countcorrectL + 1;
                elseif data.contrastLeftValues(ii) == 0
                    countcorrectNOGO = countcorrectNOGO + 1;
                end
                %count the unsuccesful ones and do it also for right, left
                %and NOGO choices
            elseif data.feedbackValues(ii) == 0
                countincorrect = countincorrect + 1;
                if data.contrastRightValues(ii) > 0
                    countincorrectR = countincorrectR + 1;
                elseif data.contrastLeftValues(ii) > 0
                    countincorrectL = countincorrectL + 1;
                elseif data.contrastLeftValues(ii) == 0
                    countincorrectNOGO = countincorrectNOGO + 1;
                end
            end
        else
            if data.responseValues(ii) == 0 && data.feedbackValues(ii) == 0
                countmissed = countmissed + 1;
            end
        %if the subject responded, calculate response time for this trial 
        end
        if data.responseValues(ii) ~= 0
            RT(iii) = data.responseTimes(ii) - data.stimulusOnTimes(ii) ...
                - deltaTime;
            iii = iii + 1;
        end
    end  
end

%finally, calculate performance as percentage of correct trials and the
%number of trials made
performance = 100*countcorrect/(countcorrect + countincorrect);
countanswered = data.trialNumValues(end) - 1 - countmissed;
performanceR = 100*countcorrectR/(countcorrectR + countincorrectR);
performanceL = 100*countcorrectL/(countcorrectL + countincorrectL);
performanceNOGO = 100*countcorrectNOGO/(countcorrectNOGO + ...
    countincorrectNOGO);

%calculate median response time
medianRT = median(RT, 'all');
disp(' ')
disp(['Subject completed ', num2str(countanswered),...
    ' trials and missed ',num2str(countmissed),' trials in ',...
    num2str(round(duration/60,0)),' minutes'])
disp(' ')
disp(['Performance is ',num2str(performance,4),'%'])
disp(['Performance for Right Go cues is ',num2str(performanceR,4),'%'])
disp(['Performance for Left Go cues is ',num2str(performanceL,4),'%'])
if countcorrectNOGO > 0 || countincorrectNOGO > 0
    disp(['Performance for No-Go cues is ',num2str(performanceNOGO,4),'%'])
end
disp(['Median response time ',num2str(medianRT,2),' seconds'])

%Plot histogram of response times
figure(1)
histogram(RT, 30);
xlabel('Response time (s)')
ylabel('Number of trials')
x0=800;
y0=400;
width=300;
height=150;
set(gcf,'position',[x0,y0,width,height])
set(gca,'box','off')

%Plot a bar chart of all response times
figure(2)
bar(RT)
xlabel('Trial')
ylabel('Response time (s)')
x0=200;
y0=300;
width=1500;
height=150;
set(gcf,'position',[x0,y0,width,height])

save('RT_2019-07-25_DO006','RT')
end