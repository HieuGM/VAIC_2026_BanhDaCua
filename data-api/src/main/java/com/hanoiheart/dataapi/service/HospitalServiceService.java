package com.hanoiheart.dataapi.service;

import com.hanoiheart.dataapi.dto.HospitalServiceDto;
import com.hanoiheart.dataapi.dto.PageResponse;
import com.hanoiheart.dataapi.dto.ServicePriceDto;
import com.hanoiheart.dataapi.entity.HospitalService;
import com.hanoiheart.dataapi.entity.ServicePrice;
import com.hanoiheart.dataapi.repository.HospitalServiceRepository;
import com.hanoiheart.dataapi.repository.ServicePriceRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional(readOnly = true)
public class HospitalServiceService {

    private final HospitalServiceRepository serviceRepository;
    private final ServicePriceRepository priceRepository;

    public HospitalServiceService(HospitalServiceRepository serviceRepository,
                                  ServicePriceRepository priceRepository) {
        this.serviceRepository = serviceRepository;
        this.priceRepository = priceRepository;
    }

    public PageResponse<HospitalServiceDto> list(String category, Long departmentId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<HospitalService> result =
                serviceRepository.findByFilter(blankToNull(category), departmentId, pageable);
        return PageResponse.of(result.map(this::toDto));
    }

    public List<ServicePriceDto> prices(Long serviceId) {
        return priceRepository.findByServiceIdOrderByAudienceAscCampusAsc(serviceId)
                .stream().map(this::toPriceDto).toList();
    }

    public HospitalServiceDto toDto(HospitalService s) {
        return new HospitalServiceDto(s.getId(), s.getCode(), s.getName(), s.getCategory(),
                s.getDepartment() == null ? null : s.getDepartment().getId(),
                s.getDescription());
    }

    private ServicePriceDto toPriceDto(ServicePrice p) {
        return new ServicePriceDto(p.getId(), p.getPriceVnd(), p.getAudience(),
                p.getCampus(), p.getEffectiveDate(), p.getSourceUrl(), p.getNote());
    }

    private String blankToNull(String s) { return (s == null || s.isBlank()) ? null : s; }
}
