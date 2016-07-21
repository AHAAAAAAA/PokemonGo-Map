FROM python:2-onbuild

ENV AUTH_SERVICE ptc
ENV USERNAME ""
ENV PASSWORD ""
ENV LOCATION ""
ENV ST 5
ENV HOST "0.0.0.0"
ENV PORT 5000
ENV GMAP_KEY ""

CMD [ "sh", "-c", "python runserver.py -a ${AUTH_SERVICE} -u ${USERNAME} -p ${PASSWORD} -l \"${LOCATION}\" -st ${ST} -P ${PORT} -k ${GMAP_KEY} -H ${HOST}" ]
